import { createRouter, createWebHistory } from 'vue-router';
import { useBookingStore } from '@/stores/booking';

// Booking Views
import HomeView from '@/views/booking/HomeView.vue';
import SearchResults from '@/views/booking/SearchResultsView.vue';
import PassengerDetails from '@/views/booking/PassengerDetailsView.vue';
import AddonsView from '@/views/booking/AddonsView.vue';
import SeatSelection from '@/views/booking/SeatSelectionView.vue';
import ReviewBooking from '@/views/booking/ReviewBookingView.vue';
import Payment from '@/views/booking/PaymentView.vue';
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

// Authentication Views
import Base_login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

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
    component: Base_login 
  },
  { 
    path: '/register', 
    name: 'Register', 
    component: Register 
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
    path: '/student/dashboard', 
    name: 'StudentDashboard', 
    component: StudentDashboard, 
    meta: { requiresAuth: true, role: 'student' }
  },
  // ✅ FIXED: Added /student/ prefix to match navigation in Student_dashboard.vue
  {
    path: '/student/activity/:id',
    name: 'StudentActivityDetails',
    component: StudentActivityDetails,
    meta: { 
      requiresAuth: true,
      role: 'student'
    },
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
    meta: { title: 'Book a Flight | Philippine Airlines' } 
  },
  { 
    path: '/check-in', 
    name: 'check-in', 
    component: () => import('../views/booking/CheckInView.vue') 
  },
  { 
    path: '/status', 
    name: 'status', 
    component: () => import('../views/booking/FlightStatusView.vue') 
  },
  { 
    path: '/flights/search', 
    name: 'SearchResults', 
    component: SearchResults 
  },
  { 
    path: '/booking/passengers', 
    name: 'PassengerDetails', 
    component: PassengerDetails 
  },
  { 
    path: '/addons', 
    name: 'Addons', 
    component: AddonsView 
  },
  { 
    path: '/addons/seats', 
    name: 'SeatSelection', 
    component: SeatSelection 
  },
  { 
    path: '/review/booking', 
    name: 'ReviewBooking', 
    component: ReviewBooking 
  },
  { 
    path: '/payment', 
    name: 'Payment', 
    component: Payment 
  },
  { 
    path: '/payment-callback', 
    name: 'PaymentCallback', 
    component: () => import('../views/booking/PaymentCallbackView.vue'), 
    meta: { requiresAuth: false } 
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
  
  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // Check for authentication token
  const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
  
  console.log('🛡️ Router Guard:', to.path);
  console.log('🔑 Token exists:', !!token);
  console.log('🔒 Requires Auth:', to.meta.requiresAuth);
  
  // Authentication Check
  if (to.meta.requiresAuth) {
    if (!token) {
      console.log('❌ No token - Redirecting to login');
      return next('/login');
    }
    
    // Optional: Check role if specified
    if (to.meta.role) {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        console.log('👤 User role:', user.role);
        
        // Role-based access control (optional - can be removed if not needed)
        // This is just a client-side check - real security is on backend
        if (user.role && user.role !== to.meta.role) {
          console.log('⚠️ Role mismatch - but allowing (backend will block if needed)');
        }
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }
  }

  // Booking flow session check
  const bookingRoutes = [
    'PassengerDetails', 
    'Addons', 
    'SeatSelection', 
    'ReviewBooking', 
    'Payment'
  ];
  
  if (bookingRoutes.includes(to.name)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      alert("Your booking session has expired or hasn't started. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
    }
  }

  next();
});

export default router;