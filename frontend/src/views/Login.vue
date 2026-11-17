<template>
    <Navbar />
    <div class="login-page">
        <div class="login-card">
            <h1>Login</h1>
            <p>Welcome to the Examination Portal</p>

            <div v-if="message" class="message">
                {{ message }}
            </div>

            <div v-if="error" class="error">
                {{ error }}
            </div>

            <form @submit.prevent="login">
                <label>Email</label>
                <input type="email" v-model="email" placeholder="Enter your email" required>

                <label>Password</label>
                <input type="password" v-model="password" placeholder="Enter your password" required>

                <button type="submit">
                    Login
                </button>
            </form>

            <p class="register-link">
                New student?
                <router-link to="/register">Create account</router-link>
            </p>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const message = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
    message.value = ''
    error.value = ''
    loading.value = true

    try {
        const response = await axios.post(
            "http://127.0.0.1:5000/login",
            {
                email: email.value,
                password: password.value
            }
        )

        message.value = response.data.message


        if (response.data.access_token) {
            localStorage.setItem("access_token", response.data.access_token)
            localStorage.setItem("role", response.data.role)

            if (response.data.role === "Admin") {
                router.push("/admin/dashboard")
            } else if (response.data.role === "Examiner") {
                router.push("/examiner/dashboard")
            } else if (response.data.role === "Student") {
                router.push("/student/dashboard")
            }
        } else {
            error.value = response.data.message
        }

    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eef7ee;
    padding: 20px;
}

.login-card {
    width: 100%;
    max-width: 420px;
    padding: 32px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

h1 {
    color: #2f5d50;
    margin-bottom: 8px;
}

label {
    display: block;
    margin-top: 15px;
    margin-bottom: 6px;
}

input {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
}

button {
    width: 100%;
    margin-top: 22px;
    padding: 12px;
    border: none;
    border-radius: 6px;
    background: #2f5d50;
    color: white;
    cursor: pointer;
}

button:disabled {
    opacity: 0.7;
}

.message {
    color: #2f5d50;
}

.error {
    color: #b42318;
}

.register-link {
    margin-top: 18px;
    text-align: center;
}
</style>