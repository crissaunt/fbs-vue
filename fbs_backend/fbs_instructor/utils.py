import json
import logging
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
from .models import Section, ScheduleNotificationLog

logger = logging.getLogger(__name__)

def check_and_send_upcoming_notifications():
    """
    Checks all sections for schedules starting in 5 minutes and sends emails.
    """
    now = timezone.now()
    # Ensure we are working with the correct local time
    local_now = timezone.localtime(now)
    
    current_day = local_now.strftime('%A')
    # We look for schedules starting in exactly 5 minutes (plus/minus 30 seconds to be safe if run on the minute)
    target_time = local_now + timedelta(minutes=5)
    target_time_str = target_time.strftime('%H:%M')
    
    print(f"Checking schedules for {current_day} at {target_time_str} (Local time: {local_now.strftime('%H:%M:%S')})")
    
    sections = Section.objects.filter(is_active=True).select_related('instructor')
    
    notifications_sent = 0
    
    for section in sections:
        if not section.schedule:
            continue
            
        try:
            schedules = json.loads(section.schedule)
            if not isinstance(schedules, list):
                continue
                
            for sched in schedules:
                sched_day = sched.get('day')
                start_time = sched.get('start_time')
                
                if sched_day == current_day and start_time == target_time_str:
                    # Check if already sent today
                    schedule_id = f"{sched_day}-{start_time}"
                    if not ScheduleNotificationLog.objects.filter(
                        section=section,
                        schedule_id=schedule_id,
                        date_sent=local_now.date()
                    ).exists():
                        
                        success = send_upcoming_schedule_email(section.instructor, section, start_time)
                        if success:
                            ScheduleNotificationLog.objects.create(
                                section=section,
                                schedule_id=schedule_id,
                                date_sent=local_now.date()
                            )
                            notifications_sent += 1


                            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error processing section {section.id}: {str(e)}")
            
    return notifications_sent

def send_upcoming_schedule_email(instructor, section, start_time):
    """Sends the 5-minute advance reminder email"""
    if not instructor.email:
        return False
        
    try:
        # Format time for display (AM/PM)
        time_obj = datetime.strptime(start_time, '%H:%M')
        display_time = time_obj.strftime('%I:%M %p')
        
        local_now = timezone.localtime(timezone.now())
        context = {
            'instructor_name': f"{instructor.first_name} {instructor.last_name}",
            'section_name': section.section_name,
            'section_code': section.section_code,
            'start_time': display_time,
            'dashboard_url': getattr(settings, 'WEBSITE_URL', 'http://localhost:5173/') + 'instructor/dashboard',
            'current_year': local_now.year,
            'formal_date': local_now.strftime('%B %d, %Y')
        }

        
        html_content = render_to_string('emails/instructor_upcoming_schedule.html', context)
        text_content = strip_tags(html_content)
        
        subject = f"URGENT: Upcoming Session in 5 Minutes - {section.section_name}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [instructor.email]
        
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print(f"Successfully sent advance notification to {instructor.email} for {section.section_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send advance email to {instructor.email}: {str(e)}")
        return False
