<template>
    <Navbar />

    <div class="page">

        <div class="heading">
            <h2>Student Dashboard</h2>
            <p>Welcome, {{ name }}</p>
        </div>

        <div class="profile-box">

            <div class="profile-heading">
                <div>
                    <h3>My Profile</h3>
                    <p>Manage your personal information</p>
                </div>

                <button v-if="profile_id" @click="showProfileForm = true">
                    Edit Profile
                </button>

                <button v-else @click="showProfileForm = true">
                    Create Profile
                </button>
            </div>

            <div v-if="profile_id && !showProfileForm" class="profile-details">
                <p><b>Address:</b> {{ address }}</p>
                <p><b>Phone:</b> {{ phone }}</p>
                <p><b>Past Experience:</b> {{ past_experience || "Not added" }}</p>
            </div>

            <form v-if="showProfileForm" @submit.prevent="saveProfile">

                <label>Address</label>
                <input
                    v-model="address"
                    type="text"
                    placeholder="Enter address"
                    required
                >

                <label>Phone</label>
                <input
                    v-model="phone"
                    type="text"
                    placeholder="Enter phone number"
                    required
                >

                <label>Past Experience</label>
                <textarea
                    v-model="past_experience"
                    placeholder="Enter past experience"
                ></textarea>

                <button type="submit">Save Profile</button>

                <button
                    type="button"
                    class="cancel"
                    @click="cancelProfile"
                >
                    Cancel
                </button>

            </form>

            <p class="message">{{ message }}</p>

        </div>

        <div class="cards">

            <div class="card">
                <h3>{{ available_examinations }}</h3>
                <p>Available Examinations</p>
            </div>

            <div class="card">
                <h3>{{ available_slots }}</h3>
                <p>Available Slots</p>
            </div>

            <div class="card">
                <h3>{{ upcoming_examinations }}</h3>
                <p>Upcoming Examinations</p>
            </div>

            <div class="card">
                <h3>{{ booked_slots }}</h3>
                <p>Booked Examination Slots</p>
            </div>

            <div class="card">
                <h3>{{ published_results }}</h3>
                <p>Published Results</p>
            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const name = ref("Student")

const profile_id = ref(null)
const address = ref("")
const phone = ref("")
const past_experience = ref("")
const showProfileForm = ref(false)
const message = ref("")

const available_examinations = ref(0)
const available_slots = ref(0)
const upcoming_examinations = ref(0)
const booked_slots = ref(0)
const published_results = ref(0)

const token = localStorage.getItem("access_token")

const headers = {
    Authorization: `Bearer ${token}`
}

const getDashboard = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/student/dashboard",
            { headers }
        )

        name.value = response.data.name || "Student"

        available_examinations.value = response.data.available_examinations || 0
        available_slots.value = response.data.available_slots || 0
        upcoming_examinations.value = response.data.upcoming_examinations || 0
        booked_slots.value = response.data.booked_slots || 0
        published_results.value = response.data.published_results || 0

    } catch (error) {
        console.log("Dashboard could not be loaded")
    }
}

const getProfile = async () => {
    try {
        const response = await axios.post(
            "http://127.0.0.1:5000/get_user_profile",
            {},
            { headers }
        )

        if (response.data.data) {
            profile_id.value = response.data.data.id
            address.value = response.data.data.address || ""
            phone.value = response.data.data.phone || ""
            past_experience.value = response.data.data.past_experience || ""
        } else {
            profile_id.value = null
        }

    } catch (error) {
        console.log("Profile could not be loaded")
    }
}

const saveProfile = async () => {
    try {
        const data = {
            address: address.value,
            phone: phone.value,
            past_experience: past_experience.value
        }

        let response

        if (profile_id.value) {
            response = await axios.post(
                "http://127.0.0.1:5000/edit_user_profile",
                data,
                { headers }
            )
        } else {
            response = await axios.post(
                "http://127.0.0.1:5000/user/submitForm",
                data,
                { headers }
            )
        }

        message.value = response.data.message

        await getProfile()
        showProfileForm.value = false

    } catch (error) {
        message.value = error.response?.data?.message || "Profile could not be saved"
    }
}

const cancelProfile = () => {
    showProfileForm.value = false
    getProfile()
    message.value = ""
}

onMounted(() => {
    getDashboard()
    getProfile()
})
</script>

<style scoped>
.page {
    padding: 25px;
    background: #f5f8f6;
    min-height: 100vh;
}

.heading {
    margin-bottom: 25px;
}

.heading h2 {
    color: #2f5d50;
    margin-bottom: 5px;
}

.heading p {
    color: #666;
}

.profile-box {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 25px;
    border: 1px solid #e5ebe7;
}

.profile-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

.profile-heading h3 {
    color: #2f5d50;
    margin-top: 0;
}

.profile-heading p {
    color: #777;
    margin-bottom: 0;
}

.profile-details {
    margin-top: 20px;
    line-height: 1.8;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 5px;
    cursor: pointer;
}

.cancel {
    background: #777;
    margin-left: 10px;
}

form {
    margin-top: 20px;
    max-width: 500px;
}

label {
    display: block;
    margin-top: 12px;
    margin-bottom: 6px;
}

input,
textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
}

textarea {
    min-height: 80px;
    margin-bottom: 15px;
}

.message {
    color: #2f5d50;
    margin-top: 12px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 8px;
    border: 1px solid #e5ebe7;
}

.card h3 {
    font-size: 26px;
    color: #2f5d50;
    margin: 0 0 8px;
}

.card p {
    color: #666;
    margin: 0;
}
</style>
