// src/services/paymentPollingService.js
import api from './api.js';

export const paymentPollingService = {
  async runFullPaymentCheck(bookingId) {
    const fullResponse = await api.get(`flightapp/check-payment-status/${bookingId}/`);
    return {
      success: fullResponse.data.success !== false,
      paid: fullResponse.data.paid === true,
      data: fullResponse.data,
      immediate: false
    };
  },

  /**
   * Simple polling for booking status with exponential backoff
   * Returns immediately if booking is confirmed
   */
  async pollBookingStatus(bookingId, options = {}) {
    const {
      maxAttempts = 15,
      interval = 2000,
      onProgress = () => { },
    } = options;

    let attempts = 0;
    let currentInterval = interval;

    const checkStatus = async () => {
      attempts++;

      try {
        console.log(`🔄 Polling booking status (attempt ${attempts}/${maxAttempts})...`);

        let response;
        try {
          response = await api.get(`flightapp/check-booking-status/${bookingId}/`);
        } catch (simpleError) {
          const fallback = await this.runFullPaymentCheck(bookingId);
          onProgress({
            attempt: attempts,
            maxAttempts,
            data: fallback.data
          });

          if (fallback.paid) {
            return {
              success: true,
              paid: true,
              data: fallback.data,
              attempts
            };
          }

          response = { data: fallback.data };
        }

        onProgress({
          attempt: attempts,
          maxAttempts,
          data: response.data
        });

        if (response.data.paid || response.data.booking_status === 'Confirmed') {
          console.log('✅ Booking confirmed!', response.data);
          return {
            success: true,
            paid: true,
            data: response.data,
            attempts: attempts
          };
        }

        if (attempts >= maxAttempts) {
          console.log('⏰ Polling timeout reached');
          return {
            success: false,
            paid: false,
            timeout: true,
            attempts: attempts,
            message: 'Payment verification timeout'
          };
        }

        // Exponential backoff: multiply interval by 1.5 each attempt, cap at 30s
        currentInterval = Math.min(currentInterval * 1.5, 30000);
        return new Promise((resolve) => {
          setTimeout(async () => {
            const result = await checkStatus();
            resolve(result);
          }, currentInterval);
        });

      } catch (error) {
        console.error('Polling error:', error);
        return {
          success: false,
          paid: false,
          error: error.message,
          attempts: attempts
        };
      }
    };

    return checkStatus();
  },

  /**
   * Check payment status once (no polling)
   */
  async checkPaymentStatusOnce(bookingId) {
    try {
      console.log(`🔍 Checking payment status for booking ${bookingId}...`);

      try {
        // Try the simple endpoint first
        const simpleResponse = await api.get(`flightapp/check-booking-status/${bookingId}/`);

        if (simpleResponse.data.paid || simpleResponse.data.booking_status === 'Confirmed') {
          return {
            success: true,
            paid: true,
            data: simpleResponse.data,
            immediate: true
          };
        }
      } catch (simpleError) {
        // Continue to full check below.
        console.warn('Simple booking-status check failed, using full payment status check.');
      }

      // Always try full check as fallback/verification path.
      return await this.runFullPaymentCheck(bookingId);

    } catch (error) {
      console.error('Payment check error:', error);
      return {
        success: false,
        paid: false,
        error: error.response?.data?.error || error.message
      };
    }
  }
};
