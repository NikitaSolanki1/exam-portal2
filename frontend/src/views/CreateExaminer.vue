
<template>
    <Navbar />

    <div class="page">
        <div class="form-card">

            <div class="heading">
                <h1>Create Examiner</h1>
                <p>Add a new examiner to the Examination Portal</p>
            </div>

            <div v-if="message" class="message">
                {{ message }}
            </div>

            <div v-if="error" class="error">
                {{ error }}
            </div>

            <form @submit.prevent="register">

                <div class="form-group">
                    <label>Examiner Name</label>
                    <input
                        type="text"
                        v-model="username"
                        placeholder="Enter examiner name"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>Email Address</label>
                    <input
                        type="email"
                        v-model="email"
                        placeholder="Enter email address"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <input
                        type="password"
                        v-model="password"
                        placeholder="Enter password"
                        required
                    >
                </div>

                <div class="buttons">
                    <button type="button" class="back-btn" @click="router.push('/admin/examiners')">
                        Back
                    </button>

                    <button type="submit" class="submit-btn">
                        Create Examiner
                    </button>
                </div>

            </form>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const message = ref('')
const error = ref('')

const register = async () => {
    message.value = ''
    error.value = ''

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            "http://127.0.0.1:5000/admin/create-examiner",
            {
                username: username.value,
                email: email.value,
                password: password.value,
                role: 'Examiner'
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === "Examiner registered successfully") {
            username.value = ''
            email.value = ''
            password.value = ''
        }

    } catch (err) {
        error.value = err.response?.data?.message || "Registration failed"
    }
}
</script>

<style scoped>
.page {
    min-height: 85vh;
    background: #eef7ee;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px 20px;
}

.form-card {
    width: 100%;
    max-width: 500px;
    background: white;
    padding: 35px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.heading {
    text-align: center;
    margin-bottom: 30px;
}

.heading h1 {
    color: #2f5d50;
    margin-bottom: 8px;
}

.heading p {
    color: #777;
    font-size: 14px;
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
}

input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
    font-size: 14px;
}

input:focus {
    outline: none;
    border-color: #2f5d50;
}

.buttons {
    display: flex;
    gap: 12px;
    margin-top: 28px;
}

.buttons button {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

.submit-btn {
    background: #2f5d50;
    color: white;
}

.submit-btn:hover {
    background: #24483e;
}

.back-btn {
    background: #e5eee8;
    color: #2f5d50;
}

.back-btn:hover {
    background: #d5e5da;
}

.message {
    background: #e8f5e9;
    color: #2f5d50;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 18px;
}

.error {
    background: #fdecec;
    color: #b42318;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 18px;
}
</style>
