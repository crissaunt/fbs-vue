import api from '@/services/api/axios';

/**
 * Downloads a file from a protected endpoint using the authenticated axios instance.
 * @param {string} url - The endpoint URL
 * @param {string} filename - The desired filename for the download
 */
export const downloadAuthenticatedFile = async (url, filename) => {
  try {
    const response = await api.get(url, {
      responseType: 'blob', // Important for binary data
    });

    // Create a temporary link element to trigger the download
    const blob = new Blob([response.data], { type: response.headers['content-type'] });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true };
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};
