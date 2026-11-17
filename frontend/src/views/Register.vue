
<template>
    <Navbar />

    <div class="register-page">
        <div class="register-card">

            <h1>Register</h1>
            <p>Create your examination portal account</p>

            <form @submit.prevent="register">

                <label>Username</label>
                <input
                    type="text"
                    v-model="username"
                    placeholder="Enter username"
                    required
                >

                <label>Email</label>
                <input
                    type="email"
                    v-model="email"
                    placeholder="Enter email"
                    required
                >

                <label>Password</label>
                <input
                    type="password"
                    v-model="password"
                    placeholder="Enter password"
                    required
                >

                <button type="submit">Register</button>

            </form>

            <p v-if="message" class="success">{{ message }}</p>
            <p v-if="error" class="error">{{ error }}</p>

            <p class="login-link">
                Already registered?
                <router-link to="/login">Login</router-link>
            </p>

        </div>
    </div>
</template>

<script setup>

import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref } from 'vue'

const username = ref('')
const email = ref('')
const password = ref('')
const message = ref('')
const error = ref('')

const register = async () => {

    message.value = ''
    error.value = ''

    try {

        const response = await axios.post(
            "http://127.0.0.1:5000/register",
            {
                name: username.value,
                email: email.value,
                password: password.value
            }
        )

        message.value = response.data.message

        username.value = ''
        email.value = ''
        password.value = ''

    } catch (err) {

        error.value = err.response?.data?.message || 'Unable to connect to server'

    }

}

</script>

<style scoped>

.register-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    background: #f5f7f5;
    padding: 20px;
}

.register-card {
    width: 100%;
    max-width: 400px;
    padding: 30px;
    background: white;
    border: 1px solid #e1e7e3;
    border-radius: 6px;
}

h1 {
    color: #2f5d50;
    margin-bottom: 8px;
}

label {
    display: block;
    margin-top: 16px;
    margin-bottom: 6px;
}

input {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
}

button {
    width: 100%;
    margin-top: 22px;
    padding: 11px;
    border: none;
    border-radius: 4px;
    background: #2f5d50;
    color: white;
    cursor: pointer;
}

button:hover {
    background: #24483d;
}

.success {
    color: #2f5d50;
}

.error {
    color: red;
}

.login-link {
    margin-top: 20px;
    text-align: center;
}

</style>
