import axios from 'axios';

const baseURL = process.env.BASEURL;
console.log('baseURL', baseURL);

const get = async (endpoint, isAuthorised = false) => {
	let headers = {};
	try {
		if (isAuthorised) {
			const token = localStorage.getItem('token');
			headers = { Authorization: `${token}` };
		}

		const response = await axios.get(baseURL + endpoint, {
			headers,
		});
		return response.data;
	} catch (error) {
		console.error('Error in GET request', error);
		throw error;
	}
};

const post = async (endpoint, data, isAuthorised = false) => {
	let headers = {};
	try {
		if (isAuthorised) {
			const token = localStorage.getItem('token');
			headers = { Authorization: `${token}` };
		}
		const response = await axios.post(baseURL + endpoint, data, {
			headers,
		});
		return response.data;
	} catch (error) {
		console.error('Error in POST request', error);
		throw error;
	}
};

const apiService = {
	login: async (data) => post('auth/login', data),
	signup: async (data) => post('auth/sign_up', data),
	listProperties: async () => get('customer/list_properties'),
	myApplications: async () => get('customer/my_applications', true),
};

export default apiService;
