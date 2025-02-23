import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',  // FastAPI 서버 주소
});

// ✅ 로그인 API 호출
export const loginUser = async (credentials) => {
  try {
    const response = await API.post('/login', credentials);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export default API;
