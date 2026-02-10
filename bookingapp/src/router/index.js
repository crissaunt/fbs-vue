import { createRouter, createWebHistory } from 'vue-router';
import { useBookingStore } from '@/stores/booking';

// 1. Import your new admin routes file
import adminRoutes from './admin';

// 2. Booking Views (Keep these or move them to a booking.js later)
import HomeView from '@/views/booking/HomeView.vue';
import SearchResults from '@/views/booking/SearchResultsView.vue';
import PassengerDetails from '@/views/booking/PassengerDetailsView.vue';
import AddonsView from '@/views/booking/AddonsView.vue';
import SeatSelection from '@/views/booking/SeatSelectionView.vue';
import ReviewBooking from '@/views/booking/ReviewBookingView.vue';
import Payment from '@/views/booking/PaymentView.vue';
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

const routes = [
  // 3. Use the Spread Operator (...) to include all admin routes
  ...adminRoutes,

  // --- Booking Routes (The main site) ---
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { title: 'Book a Flight | Philippine Airlines' }
  },
  {
    path: '/airbus-321',
    name: 'Airbus321',
    component: AirbusA321Layout
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

// Keep your router.beforeEach logic here...
router.beforeEach((to, from, next) => {
  const bookingStore = useBookingStore();
  document.title = to.meta.title || 'Philippine Airlines';

  const bookingRoutes = ['PassengerDetails', 'Addons', 'SeatSelection', 'ReviewBooking', 'Payment'];
  if (bookingRoutes.includes(to.name)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      alert("Your booking session has expired. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
    }
  }

  if (to.meta.requiresAuth && to.meta.role === 'admin') {
    const isAdminLoggedIn = !!localStorage.getItem('adminLoggedIn');
    if (!isAdminLoggedIn) {
      return next('/admin/login'); // Matches the login path in admin.js
    }
  }

  next();
});

export default router;