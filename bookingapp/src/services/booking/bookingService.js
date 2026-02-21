// src/services/bookingService.js
import api from './api'

export const bookingService = {
  async createBooking(bookingData) {
    try {
      console.log('📤 Sending booking data:', JSON.stringify(bookingData, null, 2))
      const response = await api.post('flightapp/create-booking/', bookingData)
      console.log('✅ API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error creating booking:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create booking'
      }
    }
  },

  async updateBooking(bookingId, bookingData) {
    try {
      console.log(`🔄 Updating existing booking ID: ${bookingId}`)
      console.log('📤 Update data:', JSON.stringify(bookingData, null, 2))

      // Use PATCH to update the booking
      const response = await api.patch(`flightapp/update-booking/${bookingId}/`, bookingData)
      console.log('✅ Update API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error updating booking:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to update booking'
      };
    }
  },

  async processPayment(paymentData) {
    try {
      const response = await api.post('flightapp/process-payment/', paymentData)
      return response.data
    } catch (error) {
      console.error('Error processing payment:', error.response?.data || error.message)
      throw error
    }
  },

  async getBookingDetails(bookingId) {
    try {
      const response = await api.get(`flightapp/booking/${bookingId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching booking details:', error)
      throw error
    }
  },

  formatBookingData(bookingStore) {
    console.log('🔍 Formatting booking data from store...')
    console.log('Store trip type:', bookingStore.tripType)
    console.log('Is round trip:', bookingStore.isRoundTrip)
    console.log('Store addons structure:', bookingStore.addons)

    // Ensure store is in new format
    if (bookingStore.migrateAddonsToNewFormat) {
      bookingStore.migrateAddonsToNewFormat();
    }

    // Format passengers
    const formattedPassengers = bookingStore.passengers.map(p => ({
      first_name: p.firstName || '',
      last_name: p.lastName || '',
      middle_name: p.middleName || '',
      title: p.title || 'MR',
      date_of_birth: p.dateOfBirth || this.getDefaultDOB(),
      nationality: p.nationality || 'Philippines',
      passport_number: p.passportNumber || '',
      type: p.type || 'Adult',
      key: p.key || `pax_${Math.random().toString(36).substr(2, 9)}`
    }))

    console.log('Formatted passengers:', formattedPassengers.length, 'passengers')

    // Contact info
    const contactInfo = {
      title: bookingStore.contactInfo?.title || 'MR',
      firstName: bookingStore.contactInfo?.firstName || '',
      lastName: bookingStore.contactInfo?.lastName || '',
      email: bookingStore.contactInfo?.email || '',
      phone: bookingStore.contactInfo?.phone || '',
      middleName: bookingStore.contactInfo?.middleName || ''
    }

    console.log('Formatted contact info:', contactInfo)

    // Format addons with new depart/return structure
    const formattedAddons = {
      baggage: {},
      meals: {},
      wheelchair: {},
      seats: {}
    };

    // Extract baggage addons for depart flight
    if (bookingStore.addons?.baggage?.depart) {
      Object.entries(bookingStore.addons.baggage.depart).forEach(([key, baggage]) => {
        if (baggage && baggage.id) {
          formattedAddons.baggage[key] = baggage.id;
        }
      });
    }

    // Extract meal addons for depart flight
    if (bookingStore.addons?.meals?.depart) {
      Object.entries(bookingStore.addons.meals.depart).forEach(([key, meal]) => {
        if (meal && meal.id) {
          formattedAddons.meals[key] = meal.id;
        }
      });
    }

    // Extract assistance addons for depart flight
    if (bookingStore.addons?.wheelchair?.depart) {
      Object.entries(bookingStore.addons.wheelchair.depart).forEach(([key, serviceId]) => {
        if (serviceId) {
          formattedAddons.wheelchair[key] = serviceId;
        }
      });
    }

    // Extract seats (not segmented)
    if (bookingStore.addons?.seats) {
      Object.entries(bookingStore.addons.seats).forEach(([key, seat]) => {
        if (seat && seat.id) {
          formattedAddons.seats[key] = seat.id;
        }
      });
    }

    console.log('Formatted addons (depart flight only):', formattedAddons);

    // If round trip, need to handle return flight add-ons separately
    let returnAddons = null;
    if (bookingStore.isRoundTrip) {
      returnAddons = {
        baggage: {},
        meals: {},
        wheelchair: {}
      };

      // Extract return baggage addons
      if (bookingStore.addons?.baggage?.return) {
        Object.entries(bookingStore.addons.baggage.return).forEach(([key, baggage]) => {
          if (baggage && baggage.id) {
            returnAddons.baggage[key] = baggage.id;
          }
        });
      }

      // Extract return meal addons
      if (bookingStore.addons?.meals?.return) {
        Object.entries(bookingStore.addons.meals.return).forEach(([key, meal]) => {
          if (meal && meal.id) {
            returnAddons.meals[key] = meal.id;
          }
        });
      }

      // Extract return assistance addons
      if (bookingStore.addons?.wheelchair?.return) {
        Object.entries(bookingStore.addons.wheelchair.return).forEach(([key, serviceId]) => {
          if (serviceId) {
            returnAddons.wheelchair[key] = serviceId;
          }
        });
      }

      console.log('Return flight addons:', returnAddons);
    }

    // Build complete booking data
    const bookingData = {
      trip_type: bookingStore.selectedReturn ? 'round_trip' : 'one_way',
      passengers: formattedPassengers,
      contact_info: contactInfo,
      selectedOutbound: bookingStore.selectedOutbound ? {
        id: bookingStore.selectedOutbound.id,
        schedule_id: bookingStore.selectedOutbound.schedule_id || bookingStore.selectedOutbound.id,
        flight_number: bookingStore.selectedOutbound.flight_number,
        price: parseFloat(bookingStore.selectedOutbound.price) || 0,
        class_type: bookingStore.selectedOutbound.class_type || 'Economy',
        origin: bookingStore.selectedOutbound.origin,
        destination: bookingStore.selectedOutbound.destination,
        departure_time: bookingStore.selectedOutbound.departure_time,
        airline: bookingStore.selectedOutbound.airline,
        airline_code: bookingStore.selectedOutbound.airline_code
      } : null,
      selectedReturn: bookingStore.selectedReturn ? {
        id: bookingStore.selectedReturn.id,
        schedule_id: bookingStore.selectedReturn.schedule_id || bookingStore.selectedReturn.id,
        flight_number: bookingStore.selectedReturn.flight_number,
        price: parseFloat(bookingStore.selectedReturn.price) || 0,
        class_type: bookingStore.selectedReturn.class_type || 'Economy',
        origin: bookingStore.selectedReturn.origin,
        destination: bookingStore.selectedReturn.destination,
        departure_time: bookingStore.selectedReturn.departure_time
      } : null,
      addons: formattedAddons, // Depart flight add-ons only
      return_addons: returnAddons, // Return flight add-ons
      passengerCount: {
        adult: parseInt(bookingStore.passengerCount?.adults) || 1,
        children: parseInt(bookingStore.passengerCount?.children) || 0,
        infant: parseInt(bookingStore.passengerCount?.infants) || 0
      },
      // Optional insurance selection (single-plan per booking)
      insurance_plan_id: bookingStore.addons?.insurance?.selectedPlanId || null,
      // ✅ FIX: Include activity code & practice mode so the booking is linked to the activity
      activity_code: bookingStore.activityCode || null,
      is_practice: bookingStore.isPractice || false
      // NOTE: total_amount is intentionally omitted — the backend calculates it server-side
    };

    console.log('✅ Final formatted booking data:', JSON.stringify(bookingData, null, 2));
    return bookingData;
  },

  // Helper to get default date of birth (20 years ago)
  getDefaultDOB() {
    const date = new Date()
    date.setFullYear(date.getFullYear() - 20)
    return date.toISOString().split('T')[0]  // YYYY-MM-DD format
  },

  /**
   * Fetch the authoritative price from the backend before booking creation.
   * Use this on the Review Booking page to display the real total.
   */
  async calculatePrice(bookingStore) {
    try {
      const payload = this.formatBookingData(bookingStore)
      const response = await api.post('flightapp/calculate-price/', payload)
      if (response.data?.success) {
        return {
          success: true,
          totalAmount: response.data.total_amount,
          breakdown: response.data.breakdown,
          currency: response.data.currency
        }
      }
      return { success: false, error: response.data?.error || 'Failed to calculate price' }
    } catch (error) {
      console.error('❌ Error calculating price:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to calculate price'
      }
    }
  }
}