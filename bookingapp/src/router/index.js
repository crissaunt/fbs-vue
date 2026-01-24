import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/booking/HomeView.vue';
import SearchResults from '@/views/booking/SearchResultsView.vue';
import PassengerDetails from '@/views/booking/PassengerDetailsView.vue';
import AddonsView from '@/views/booking/AddonsView.vue';
import SeatSelection from '@/views/booking/SeatSelectionView.vue';
import ReviewBooking from '@/views/booking/ReviewBookingView.vue';
import Payment from '@/views/booking/PaymentView.vue';
import BookingDetails from '@/views/booking/BookingDetailsView.vue';
import { useBookingStore } from '@/stores/booking';
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

const routes = [
 
  {
    path: '/airbus-321', // The URL you will type
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
    // Route level code-splitting (Lazy loading)
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
    path:'/booking/passengers',
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
    path: '/booking/:reference',
    name: 'BookingDetails',
    component: () => import('@/views/booking/BookingDetailsView.vue'),
    props: true
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

// Optional: Change page title dynamically
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Philippine Airlines';
  next();
});
// In router/index.js, add this before export:
const bookingRoutes = [
  'PassengerDetails',
  'Addons',
  'SeatSelection',
  'ReviewBooking',
  'Payment'
];

router.beforeEach((to, from, next) => {
  const bookingStore = useBookingStore();
  
  // Check if route requires active booking session
  if (bookingRoutes.includes(to.name)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      // Session expired or doesn't exist
      alert("Your booking session has expired or hasn't started. Please start a new search.");
      bookingStore.resetBooking();
      next('/');
      return;
    }
  }
  
  document.title = to.meta.title || 'Philippine Airlines';
  next();
});
export default router;