// src/router/admin.js
const adminRoutes = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/login.vue'),
    meta: { title: 'Admin Login' }
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/adminlayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/admindashboard.vue'),
        meta: { title: 'Dashboard' }
      },

      // --- Manage Flight ---
      {
        path: 'manage-flight/routes',
        name: 'ManageRoutes',
        component: () => import('@/views/admin/manage_flight/routes.vue'),
        meta: { title: 'Flight Routes' }
      },
      {
        path: 'manage-flight/flights',
        name: 'ManageFlights',
        component: () => import('@/views/admin/manage_flight/flights.vue'),
        meta: { title: 'Flight Management' }
      },
      {
        path: 'manage-flight/schedules',
        name: 'ManageSchedules',
        component: () => import('@/views/admin/manage_flight/schedules.vue'),
        meta: { title: 'Flight Schedules' }
      },
      {
        path: 'manage-flight/seats',
        name: 'ManageSeats',
        component: () => import('@/views/admin/manage_flight/seats.vue'),
        meta: { title: 'Seat Maps' }
      },

      // --- Assets ---
      {
        path: 'assets/airports',
        name: 'AdminAirports',
        component: () => import('@/views/admin/assets/airports.vue'),
        meta: { title: 'Airports' }
      },
      {
        path: 'assets/add-ons',
        name: 'AdminAddOns',
        component: () => import('@/views/admin/assets/addons.vue'),
        meta: { title: 'Add-ons' }
      },
      {
        path: 'assets/seat-classes',
        name: 'AdminSeatClasses',
        component: () => import('@/views/admin/assets/seat_classes.vue'),
        meta: { title: 'Seat Classes' }
      },
      {
        path: 'assets/airlines',
        name: 'AdminAirlines',
        component: () => import('@/views/admin/assets/airlines.vue'),
        meta: { title: 'Airlines' }
      },
      {
        path: 'assets/aircraft',
        name: 'AdminAircraft',
        component: () => import('@/views/admin/assets/aircraft.vue'),
        meta: { title: 'Aircraft' }
      },

      // --- Booking ---
      {
        path: 'booking/details',
        name: 'AdminBookingDetails',
        component: () => import('@/views/admin/booking/details.vue'),
        meta: { title: 'Booking Details' }
      },
      {
        path: 'booking/list',
        name: 'AdminBookingsList',
        component: () => import('@/views/admin/booking/list.vue'),
        meta: { title: 'Bookings' }
      },
      {
        path: 'booking/payments',
        name: 'AdminPayments',
        component: () => import('@/views/admin/booking/payments.vue'),
        meta: { title: 'Payments' }
      },

      // --- Passenger ---
      {
        path: 'passenger/list',
        name: 'AdminPassengerList',
        component: () => import('@/views/admin/passenger/list.vue'),
        meta: { title: 'Passengers' }
      },
      {
        path: 'passenger/check-ins',
        name: 'AdminCheckIns',
        component: () => import('@/views/admin/passenger/check_ins.vue'),
        meta: { title: 'Check-ins' }
      },

      // --- Student Info ---
      {
        path: 'student-info/list',
        name: 'AdminStudentList',
        component: () => import('@/views/admin/student_info/list.vue'),
        meta: { title: 'Students' }
      },
      {
        path: 'student-info/track-log',
        name: 'AdminTrackLog',
        component: () => import('@/views/admin/student_info/track_log.vue'),
        meta: { title: 'Track Log' }
      },

      // --- Instructor Info ---
      {
        path: 'instructor-info/list',
        name: 'AdminInstructorList',
        component: () => import('@/views/admin/instructor_info/list.vue'),
        meta: { title: 'Instructors' }
      },

      // --- Manage Tax ---
      {
        path: 'manage-tax/airport-fee',
        name: 'AdminTaxAirportFee',
        component: () => import('@/views/admin/manage_tax/airport_fee.vue'),
        meta: { title: 'Airport Fee' }
      },
      {
        path: 'manage-tax/tax-type',
        name: 'AdminTaxType',
        component: () => import('@/views/admin/manage_tax/tax_type.vue'),
        meta: { title: 'Tax Types' }
      },
      {
        path: 'manage-tax/airline-tax',
        name: 'AdminAirlineTax',
        component: () => import('@/views/admin/manage_tax/airline_tax.vue'),
        meta: { title: 'Airline Tax' }
      },
      {
        path: 'manage-tax/travel-tax',
        name: 'AdminTravelTax',
        component: () => import('@/views/admin/manage_tax/travel_tax.vue'),
        meta: { title: 'Travel Tax' }
      },
      {
        path: 'manage-tax/booking-tax',
        name: 'AdminBookingTax',
        component: () => import('@/views/admin/manage_tax/booking_tax.vue'),
        meta: { title: 'Booking Tax' }
      }
    ]
  }
];

export default adminRoutes;
