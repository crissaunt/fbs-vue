import { defineStore } from 'pinia';

export const useBookingStore = defineStore('booking', {
  state: () => ({
    booking_id: null,
    booking_reference: null,
    booking_status: null,
    booking_total: 0,
    selectedOutbound: null,
    selectedReturn: null,
    tripType: 'one_way',
    passengerCount: {
      adults: 1,
      children: 0,
      infants: 0,
    }, 
    passengers: [],

    contactInfo: {
      title: '',
      firstName: '',
      middleName: '',
      lastName: '',
      email: '',
      phone: ''
    },
    
    // UPDATED: New structure for depart/return add-ons
    addons: {
      baggage: {
        depart: {},  // { passengerKey: baggageObject }
        return: {}   // { passengerKey: baggageObject }
      },     
      meals: {
        depart: {},  // { passengerKey: mealObject }
        return: {}   // { passengerKey: mealObject }
      },       
      wheelchair: {
        depart: {},  // { passengerKey: assistanceId }
        return: {}   // { passengerKey: assistanceId }
      },   
      seats: {}      // Keep seats as-is (usually applies to all flights)
    },
    
    sessionExpiry: null,
  }),
  persist: true,
  
  getters: {
    isRoundTrip: (state) => state.tripType === 'round_trip',
    isOneWay: (state) => state.tripType === 'one_way',
    
    combinedBasePrice: (state) => {
      const outbound = parseFloat(state.selectedOutbound?.price || 0);
      const returnPrice = state.tripType === 'round_trip' ? parseFloat(state.selectedReturn?.price || 0) : 0;
      return outbound + returnPrice;
    },
    
    grandTotalForAdults(state) {
      return this.combinedBasePrice * state.passengerCount.adults;
    },
    
    grandTotalForChildren(state) {
      return this.combinedBasePrice * state.passengerCount.children;
    },
    
    grandTotalForInfants(state) {
      return (this.combinedBasePrice * 0.5) * state.passengerCount.infants;
    },
    
    // UPDATED: Grand total calculation for new structure
    grandTotal: (state) => {
      let total = 0;

      // 1. Base Flight Prices
      if (state.selectedOutbound?.price) {
        total += parseFloat(state.selectedOutbound.price);
      }

      // Only add return flight price if it's a round trip AND return flight exists
      if (state.tripType === 'round_trip' && state.selectedReturn?.price) {
        total += parseFloat(state.selectedReturn.price);
      }
      
      // Multiply by number of passengers (adults + children)
      const travelerCount = (state.passengerCount.adults || 0) + (state.passengerCount.children || 0);
      total = total * travelerCount;

      // 2. Add Baggage (depart + return for round trips)
      const baggageSegments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      baggageSegments.forEach(segment => {
        Object.values(state.addons.baggage[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // 3. Add Meals (depart + return for round trips)
      baggageSegments.forEach(segment => {
        Object.values(state.addons.meals[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // 4. Add Assistance (depart + return for round trips)
      baggageSegments.forEach(segment => {
        Object.values(state.addons.wheelchair[segment] || {}).forEach(serviceId => {
          // Note: Assistance services are free, but if they had price:
          // const service = findServiceById(serviceId);
          // if (service?.price) total += parseFloat(service.price);
        });
      });

      // 5. Add Seats (usually applies to all flights, so not segmented)
      Object.values(state.addons.seats).forEach(seat => {
        if (seat?.final_price) total += parseFloat(seat.final_price);
      });

      return total;
    },
    
    isFlightSelectionComplete: (state) => {
      if (state.tripType === 'one_way') {
        return state.selectedOutbound !== null;
      } else if (state.tripType === 'round_trip') {
        return state.selectedOutbound !== null && state.selectedReturn !== null;
      }
      return false;
    },
    
    // NEW: Helper to get total add-ons price
    totalAddonsPrice: (state) => {
      let total = 0;
      const segments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      
      // Baggage
      segments.forEach(segment => {
        Object.values(state.addons.baggage[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });
      
      // Meals
      segments.forEach(segment => {
        Object.values(state.addons.meals[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });
      
      // Seats
      Object.values(state.addons.seats).forEach(seat => {
        if (seat?.final_price) total += parseFloat(seat.final_price);
      });
      
      return total;
    }
  },
  
  actions: {
    // Session management methods
    startSession() {
      this.sessionExpiry = Date.now() + (15 * 60 * 1000); // 15 minutes
      console.log('🔄 Session refreshed, expires at:', new Date(this.sessionExpiry).toLocaleString());
    },
    
    checkSession() {
      if (!this.sessionExpiry) {
        return { valid: false, reason: 'No active session', expired: true };
      }
      
      const now = Date.now();
      const timeLeft = this.sessionExpiry - now;
      const minutesLeft = Math.floor(timeLeft / (60 * 1000));
      const secondsLeft = Math.floor((timeLeft % (60 * 1000)) / 1000);
      
      if (timeLeft <= 0) {
        this.resetBooking();
        return { 
          valid: false, 
          reason: 'Session expired',
          expired: true 
        };
      }
      
      return { 
        valid: true, 
        timeLeft, 
        minutesLeft, 
        secondsLeft,
        expiresAt: new Date(this.sessionExpiry).toLocaleString()
      };
    },
    
    initSession() {
      // If no expiry time is set, assume session is starting now
      if (!this.sessionExpiry) {
        this.startSession();
      }
    },
    
    setTripType(type) {
      console.log('🟢 Setting trip type in Pinia:', type);
      const normalizedType = type === 'round-trip' ? 'round_trip' : type;
      this.tripType = normalizedType;
      
      // If switching from round trip to one way, clear return flight
      if (normalizedType === 'one_way' && this.selectedReturn) {
        console.log('Clearing return flight due to trip type change');
        this.selectedReturn = null;
        
        // Also clear return add-ons
        this.addons.baggage.return = {};
        this.addons.meals.return = {};
        this.addons.wheelchair.return = {};
      }
    },

    setPassengerCount(counts) {
      this.passengerCount.adults = counts.adult;
      this.passengerCount.children = counts.children;
      this.passengerCount.infants = counts.infant;
    },

    selectFlight(flight, type = 'outbound') {
      if (type === 'outbound') {
        this.selectedOutbound = flight;
        console.log('✅ Outbound flight selected:', flight.flight_number);
      } else {
        if (this.tripType === 'round_trip') {
          this.selectedReturn = flight;
          console.log('✅ Return flight selected:', flight.flight_number);
        } else {
          console.warn('Cannot select return flight for one-way trip');
        }
      }
    },

    setPassengers(passengerList) {
      console.log('🟢 STORING PASSENGERS IN PINIA:');
      
      const processedPassengers = passengerList.map((passenger, index) => {
        const key = passenger.key || `pax_${index + 1}`;
        
        return {
          key: key,
          firstName: passenger.firstName || '',
          lastName: passenger.lastName || '',
          middleName: passenger.middleName || '',
          title: passenger.title || 'MR',
          dateOfBirth: passenger.dateOfBirth || this.getDefaultDOB(),
          nationality: passenger.nationality || 'Philippines',
          passportNumber: passenger.passportNumber || '',
          type: passenger.type || 'Adult'
        };
      });
      
      this.passengers = processedPassengers;
    },

    getDefaultDOB() {
      const date = new Date();
      date.setFullYear(date.getFullYear() - 20);
      return date.toISOString().split('T')[0];
    },
    
    setContactInfo(info) {
      this.contactInfo = { ...this.contactInfo, ...info };
    },
    
    // ========== UPDATED ADD-ON METHODS ==========
    
    // Set all addons at once
    setAddons(addonData) {
      this.addons = {
        baggage: addonData.baggage || { depart: {}, return: {} },
        meals: addonData.meals || { depart: {}, return: {} },
        wheelchair: addonData.wheelchair || { depart: {}, return: {} },
        seats: addonData.seats || {}
      };
    },
    
    // Update baggage with segment support
    updateBaggageAddon(passengerKey, baggageData, segment = 'depart') {
      if (!this.addons.baggage[segment]) {
        this.addons.baggage[segment] = {};
      }
      this.addons.baggage[segment][passengerKey] = baggageData;
    },
    
    // Update meal with segment support
    updateMealAddon(passengerKey, mealData, segment = 'depart') {
      if (!this.addons.meals[segment]) {
        this.addons.meals[segment] = {};
      }
      this.addons.meals[segment][passengerKey] = mealData;
    },
    
    // Update assistance with segment support
    updateAssistanceAddon(passengerKey, serviceId, segment = 'depart') {
      if (!this.addons.wheelchair[segment]) {
        this.addons.wheelchair[segment] = {};
      }
      this.addons.wheelchair[segment][passengerKey] = serviceId;
    },
    
    // Remove methods with segment support
    removeBaggageAddon(passengerKey, segment = 'depart') {
      if (this.addons.baggage[segment] && this.addons.baggage[segment][passengerKey]) {
        delete this.addons.baggage[segment][passengerKey];
      }
    },
    
    removeMealAddon(passengerKey, segment = 'depart') {
      if (this.addons.meals[segment] && this.addons.meals[segment][passengerKey]) {
        delete this.addons.meals[segment][passengerKey];
      }
    },
    
    removeAssistanceAddon(passengerKey, segment = 'depart') {
      if (this.addons.wheelchair[segment] && this.addons.wheelchair[segment][passengerKey]) {
        delete this.addons.wheelchair[segment][passengerKey];
      }
    },
    
    // Seats (usually not segmented, applies to all flights)
    assignSeat(passengerKey, seatData) {
      this.addons.seats = {
        ...this.addons.seats,
        [passengerKey]: {
          id: seatData.id,
          seat_code: seatData.seat_number || seatData.seat_code, 
          final_price: parseFloat(seatData.final_price) || 0, 
          seat_class: {
            name: seatData.seat_class_name || seatData.seat_class?.name
          }
        }
      };
    },
    
    removeSeat(passengerKey) {
      if (this.addons.seats && this.addons.seats[passengerKey]) {
        const newSeats = { ...this.addons.seats };
        delete newSeats[passengerKey];
        this.addons.seats = newSeats;
      }
    },
    
    // NEW: Copy add-ons from depart to return (for round trips)
    copyAddonsToReturn() {
      if (!this.isRoundTrip) return;
      
      console.log('📋 Copying add-ons from depart to return segment');
      
      // Copy baggage
      this.addons.baggage.return = { ...this.addons.baggage.depart };
      
      // Copy meals
      this.addons.meals.return = { ...this.addons.meals.depart };
      
      // Copy assistance
      this.addons.wheelchair.return = { ...this.addons.wheelchair.depart };
    },
    
    // Clear all addons
    clearAllAddons() {
      this.addons = {
        baggage: { depart: {}, return: {} },
        meals: { depart: {}, return: {} },
        wheelchair: { depart: {}, return: {} },
        seats: {}
      };
    },
    
    // Clear only return add-ons
    clearReturnAddons() {
      this.addons.baggage.return = {};
      this.addons.meals.return = {};
      this.addons.wheelchair.return = {};
    },
    
    clearAllSeats() {
      this.addons.seats = {};
    },
    
    saveBookingConfirmation(bookingData) {
      this.booking_id = bookingData.booking_id;
      this.booking_reference = bookingData.booking_reference;
      this.booking_status = bookingData.status;
      
      // IMPORTANT: Use the grandTotal from store instead of backend response
      // Backend might return wrong amount, but store has correct calculation
      this.booking_total = this.grandTotal || parseFloat(bookingData.total_amount) || 0;
      
      this.sessionExpiry = Date.now() + (15 * 60 * 1000);
      
      console.log('✅ Booking confirmation saved:', {
        booking_id: this.booking_id,
        booking_reference: this.booking_reference,
        store_grand_total: this.grandTotal,
        backend_total_amount: bookingData.total_amount,
        saved_booking_total: this.booking_total,
        expiry: new Date(this.sessionExpiry).toLocaleString()
      });
    },
    
    resetBooking() {
      this.$reset();
      localStorage.removeItem('booking');
      localStorage.removeItem('current_booking');
      localStorage.removeItem('payment_session');
      
      console.log("🧹 Booking Store and LocalStorage have been cleared.");
    },
    
    // NEW: Migration helper for old data format
    migrateAddonsToNewFormat() {
      // Check if we have old flat structure
      if (this.addons.baggage && !this.addons.baggage.depart) {
        console.log('🔄 Migrating add-ons to new format...');
        
        const oldBaggage = this.addons.baggage;
        const oldMeals = this.addons.meals;
        const oldAssistance = this.addons.wheelchair;
        
        // Convert to new structure
        this.addons.baggage = { depart: { ...oldBaggage }, return: {} };
        this.addons.meals = { depart: { ...oldMeals }, return: {} };
        this.addons.wheelchair = { depart: { ...oldAssistance }, return: {} };
        
        // If round trip, copy to return
        if (this.isRoundTrip) {
          this.addons.baggage.return = { ...oldBaggage };
          this.addons.meals.return = { ...oldMeals };
          this.addons.wheelchair.return = { ...oldAssistance };
        }
        
        console.log('✅ Migration complete');
      }
    }
  }
});