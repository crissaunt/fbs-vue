// src/services/paymentPollingService.js
import api from './api.js';

export const paymentPollingService = {
  /**
   * Simple polling for booking status
   * Returns immediately if booking is confirmed
   */
  async pollBookingStatus(bookingId, options = {}) {
    const {
      maxAttempts = 30,
      interval = 2000,
      onProgress = () => {},
      immediateFirstCheck = true
    } = options;
    
    let attempts = 0;
    
    const checkStatus = async () => {
      attempts++;
      
      try {
        console.log(`🔄 Polling booking status (attempt ${attempts}/${maxAttempts})...`);
        
        // Use the simple endpoint that doesn't search PayMongo
        const response = await api.get(`check-booking-status/${bookingId}/`);
        
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
        
        // Continue polling
        return new Promise((resolve) => {
          setTimeout(async () => {
            const result = await checkStatus();
            resolve(result);
          }, interval);
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
    
    // Start polling
    return checkStatus();
  },
  
  /**
   * Check payment status once (no polling)
   */
  async checkPaymentStatusOnce(bookingId) {
    try {
      console.log(`🔍 Checking payment status for booking ${bookingId}...`);
      
      // Try the simple endpoint first
      const simpleResponse = await api.get(`check-booking-status/${bookingId}/`);
      
      if (simpleResponse.data.paid || simpleResponse.data.booking_status === 'Confirmed') {
        return {
          success: true,
          paid: true,
          data: simpleResponse.data,
          immediate: true
        };
      }
      
      // If not confirmed, try the full check
      const fullResponse = await api.get(`check-payment-status/${bookingId}/`);
      
      return {
        success: fullResponse.data.success !== false,
        paid: fullResponse.data.paid === true,
        data: fullResponse.data,
        immediate: false
      };
      
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