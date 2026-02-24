import { createRouter, createWebHistory } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import AuthStorage from '@/utils/authStorage';

// Booking Views
import HomeView from '@/views/booking/HomeView.vue';
import SearchResults from '@/views/booking/SearchResultsView.vue';
import PassengerDetails from '@/views/booking/PassengerDetailsView.vue';
import AddonsView from '@/views/booking/AddonsView.vue';
import SeatSelection from '@/views/booking/SeatSelectionView.vue';
import ProfileView from '@/views/Profile/ProfileView.vue';
import ReviewBooking from '@/views/booking/ReviewBookingView.vue';
import Payment from '@/views/booking/PaymentView.vue';
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

// Authentication Views
// import Base_login from '@/views/Login.vue';
// import Register from '@/views/Register.vue';

// Instructor Views
import InstructorDashboard from '@/views/Instructor/instructor_dashboard.vue';
import Activity_details from '@/views/Instructor/Activity/Activity_details.vue';

// Student Views
import StudentDashboard from '@/views/Student/Student_dashboard.vue';
import StudentActivityDetails from '@/views/Student/Activities/Student_activity_details.vue'

const routes = [
  {
    path: '/login',
    name: 'instructor_login',
    component: () => import('@/views/Login.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/instructor/dashboard',
    name: 'instructor_dashboard',
    component: InstructorDashboard,
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/section/:id',
    name: 'SectionDetails',
    component: () => import('@/views/Instructor/Section_details.vue'),
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/section/:id/people',
    name: 'SectionPeople',
    component: () => import('@/views/Instructor/Section_student_list.vue'),
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/activity/:activityId',
    name: 'ActivityDetails',
    component: Activity_details,
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
<<<<<<< HEAD
    path: '/instructor/activity/:activityId/student/:studentId/score',
    name: 'InstructorStudentScore',
    component: () => import('@/views/Instructor/Activity/instructor_students_score.vue'),
    meta: { requiresAuth: true, role: 'instructor' }
=======
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
>>>>>>> 180f93bb201c35eddd6b7c4897a717198d49311f
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/activity/:id',
    name: 'StudentActivityDetails',
    component: StudentActivityDetails,
    meta: { requiresAuth: true, role: 'student' },
    props: true
  },
  {
    path: '/airbus-321',
    name: 'Airbus321',
    component: AirbusA321Layout
  },
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      layout: 'BookingLayout',
      title: 'Book a Flight | Philippine Airlines',
      requiresAuth: true,
      isBookingProtected: true // Needs activity code check
    }
  },
  {
    path: '/check-in',
    name: 'check-in',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('../views/booking/CheckInView.vue')
  },
  {
    path: '/status',
    name: 'status',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('../views/booking/FlightStatusView.vue')
  },
  {
    path: '/flights/search',
    name: 'SearchResults',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: SearchResults
  },
  {
    path: '/booking/passengers',
    name: 'PassengerDetails',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: PassengerDetails
  },
  {
    path: '/addons',
    name: 'Addons',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: AddonsView
  },
  {
    path: '/addons/seats',
    name: 'SeatSelection',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: SeatSelection
  },
  {
    path: '/review/booking',
    name: 'ReviewBooking',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: ReviewBooking
  },
  {
    path: '/payment',
    name: 'Payment',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: Payment
  },
  {
    path: '/payment-callback',
    name: 'PaymentCallback',
    meta: { layout: 'BookingLayout', requiresAuth: false },
    component: () => import('../views/booking/PaymentCallbackView.vue')
  },
  {
    path: '/booking-success',
    name: 'BookingSuccess',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('@/views/booking/BookingSuccessView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// ==========================================
// NAVIGATION GUARD
// ==========================================
router.beforeEach((to, from, next) => {
  const bookingStore = useBookingStore();
  const notificationStore = useNotificationStore();

  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  const token = AuthStorage.getToken();
  const userRole = AuthStorage.getRole();

  console.log('🛡️ Router Guard:', to.path);
  console.log('🔑 Token exists:', !!token);
  console.log('🔒 Requires Auth:', to.meta.requiresAuth);

<<<<<<< HEAD
  // REDIRECT AUTHENTICATED USERS AWAY FROM LOGIN/REGISTER
  if ((to.name === 'instructor_login' || to.name === 'Register') && token) {
    console.log('👤 Authenticated user attempting to visit login/register - Redirecting...');
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const role = localStorage.getItem('role') || user.role;

      console.log('Detected role for redirection:', role);

      if (role === 'instructor') {
=======
  // 1. Guest Only Routes (Login/Register)
  if (to.matched.some(record => record.meta.guestOnly)) {
    if (token) {
      console.log('👤 Authenticated user attempting to visit guest route - Redirecting...');
      if (userRole === 'instructor') {
>>>>>>> 180f93bb201c35eddd6b7c4897a717198d49311f
        return next('/instructor/dashboard');
      } else if (role === 'student') {
        return next('/student/dashboard');
      } else if (role === 'admin') {
        // Direct to home or a custom admin path if it existed, but for now / is safest if Vue admin is missing
        return next('/');
      } else {
        return next('/');
      }
    }
    return next();
  }

  // 2. Requires Authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      console.log('❌ No token - Redirecting to login');
      return next('/login');
    }

    // Role-based Route Protection
    if (to.meta.role && userRole && userRole !== to.meta.role) {
      console.warn(`⛔ User role '${userRole}' blocked from accessing '${to.meta.role}' route`);
      notificationStore.error('You do not have permission to access that page.');
      if (userRole === 'instructor') {
        return next('/instructor/dashboard');
      } else {
        return next('/student/dashboard');
      }
    }

    // Additional Check: Instructors cannot access booking flow
    if (to.meta.isBookingProtected && userRole === 'instructor') {
      console.warn('⛔ Instructor attempted to access booking flow:', to.path);
      return next('/instructor/dashboard');
    }
  }

  // 3. Booking Protection (Activity Code / Practice Mode)
  if (to.matched.some(record => record.meta.isBookingProtected)) {
    if (!bookingStore.hasActivityCodeValidation) {
      console.log('❌ Authenticated user without activity code in booking area');
      notificationStore.info('Please enter an activity code or select practice mode to start booking.');
      return next('/student/dashboard');
    }
  }

  // 4. Prevent accessing Student Dashboard during active booking
  if (to.path.startsWith('/student/dashboard') && bookingStore.hasActivityCodeValidation) {
    console.log('⚠️ Active booking session detected - Blocking dashboard access');
    notificationStore.warn('Please end your activity session before returning to the dashboard.');
    return next('/');
  }

  // 5. Active Booking Session Expiry Check
  if (to.matched.some(record => record.meta.requireActiveBookingSession)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      notificationStore.error("Your booking session has expired or hasn't started. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
    }
  }

  next();
});

export default router;
