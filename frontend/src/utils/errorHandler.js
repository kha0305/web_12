/**
 * Extract error message from API response
 * Handles different error formats from FastAPI/Pydantic
 * @param {Error} error - Axios error object
 * @param {string} defaultMessage - Default message if no specific error found
 * @returns {string} - User-friendly error message
 */
export const getErrorMessage = (error, defaultMessage = 'Có lỗi xảy ra') => {
  const detail = error.response?.data?.detail;
  
  // Handle validation errors (array of error objects)
  if (Array.isArray(detail) && detail.length > 0) {
    // Extract first error message
    return detail[0].msg || detail[0].message || defaultMessage;
  }
  
  // Handle string error messages
  if (typeof detail === 'string') {
    return detail;
  }
  
  // Handle object error (single validation error)
  if (detail && typeof detail === 'object' && detail.msg) {
    return detail.msg;
  }
  
  // Return default message
  return defaultMessage;
};

/**
 * Show error toast with proper message extraction
 * @param {Error} error - Axios error object
 * @param {Function} toastFn - Toast function (e.g., toast.error)
 * @param {string} defaultMessage - Default message if no specific error found
 */
export const showErrorToast = (error, toastFn, defaultMessage = 'Có lỗi xảy ra') => {
  const message = getErrorMessage(error, defaultMessage);
  toastFn(message);
};
