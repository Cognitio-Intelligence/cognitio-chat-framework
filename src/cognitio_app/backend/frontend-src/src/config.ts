// Get the API base URL from the window.APP_CONFIG or use a default
const API_BASE_URL = (window as any).APP_CONFIG?.API_BASE_URL || 'http://127.0.0.1:3927/api/v1';

export const config = {
    API_BASE_URL,
    WEBLLM_API: {
        POLL: `${API_BASE_URL}/webllm/poll/`,
        SUBMIT: `${API_BASE_URL}/webllm/submit/`,
        CHAT: `${API_BASE_URL}/webllm/chat/`,
        STATUS: `${API_BASE_URL}/webllm/status/`,
    }
};
