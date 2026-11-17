
<template>
    <Navbar />

    <div class="page">

        <div class="heading">
            <h2>My Profile</h2>
            <p>View and manage your examiner profile</p>
        </div>

        <div v-if="message" class="message">
            {{ message }}
        </div>

        <div class="profile-box" v-if="!loading">

            <div v-if="!isEditing">

                <div class="profile-heading">
                    <h3>Examiner Details</h3>

                    <button v-if="profileExists" @click="editProfile">
                        Edit Profile
                    </button>
                </div>

                <div class="details">
                    <div>
                        <label>Name</label>
                        <p>{{ profile.name }}</p>
                    </div>

                    <div>
                        <label>Email</label>
                        <p>{{ profile.email }}</p>
                    </div>

                    <div>
                        <label>Department</label>
                        <p>{{ profile.department || "Not added" }}</p>
                    </div>

                    <div>
                        <label>Phone</label>
                        <p>{{ profile.phone || "Not added" }}</p>
                    </div>

                    <div>
                        <label>Address</label>
                        <p>{{ profile.address || "Not added" }}</p>
                    </div>

                    <div>
                        <label>Past Experience</label>
                        <p>{{ profile.past_experience || "Not added" }}</p>
                    </div>

                    <div v-if="profileExists">
                        <label>Status</label>
                        <p>{{ profile.status }}</p>
                    </div>
                </div>

                <div v-if="!profileExists" class="create-message">
                    <p>Your profile has not been created yet.</p>
                    <button @click="isEditing = true">
                        Create Profile
                    </button>
                </div>

            </div>

            <div v-else>

                <h3>{{ profileExists ? "Edit Profile" : "Create Profile" }}</h3>

                <form @submit.prevent="saveProfile">

                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" v-model="profile.name" disabled>
                    </div>

                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" v-model="profile.email" disabled>
                    </div>

                    <div class="form-group">
                        <label>Department</label>
                        <input
                            type="text"
                            v-model="profile.department"
                            placeholder="Enter department"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Phone</label>
                        <input
                            type="text"
                            v-model="profile.phone"
                            placeholder="Enter phone number"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Address</label>
                        <textarea
                            v-model="profile.address"
                            placeholder="Enter address"
                            required
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label>Past Experience</label>
                        <textarea
                            v-model="profile.past_experience"
                            placeholder="Enter your past experience"
                        ></textarea>
                    </div>

                    <div class="buttons">
                        <button type="submit" :disabled="saving">
                            {{ saving ? "Saving..." : "Save Profile" }}
                        </button>

                        <button
                            type="button"
                            class="cancel-btn"
                            @click="cancelEdit"
                        >
                            Cancel
                        </button>
                    </div>

                </form>

            </div>

        </div>

        <p v-if="loading" class="loading">Loading profile...</p>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const profileExists = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const saving = ref(false)
const message = ref("")

const profile = ref({
    name: "",
    email: "",
    department: "",
    phone: "",
    address: "",
    past_experience: "",
    status: ""
})

const headers = {
    Authorization: "Bearer " + localStorage.getItem("access_token")
}

const getProfile = async () => {

    loading.value = true

    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/profile",
            { headers }
        )

        profileExists.value = response.data.profile_exists

        profile.value = {
            name: response.data.name || "",
            email: response.data.email || "",
            department: response.data.department || "",
            phone: response.data.phone || "",
            address: response.data.address || "",
            past_experience: response.data.past_experience || "",
            status: response.data.status || ""
        }

        if (!profileExists.value) {
            isEditing.value = false
        }

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load profile"
    }

    loading.value = false
}

const editProfile = () => {
    message.value = ""
    isEditing.value = true
}

const cancelEdit = () => {
    message.value = ""
    getProfile()
    isEditing.value = false
}

const saveProfile = async () => {

    saving.value = true
    message.value = ""

    try {

        if (profileExists.value) {

            const response = await axios.put(
                "http://127.0.0.1:5000/examiner/profile",
                {
                    department: profile.value.department,
                    phone: profile.value.phone,
                    address: profile.value.address,
                    past_experience: profile.value.past_experience
                },
                { headers }
            )

            message.value = response.data.message

        } else {

            const response = await axios.post(
                "http://127.0.0.1:5000/examiner/profile",
                {
                    department: profile.value.department,
                    phone: profile.value.phone,
                    address: profile.value.address,
                    past_experience: profile.value.past_experience
                },
                { headers }
            )

            message.value = response.data.message
        }

        await getProfile()
        isEditing.value = false

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to save profile"
    }

    saving.value = false
}

onMounted(() => {
    getProfile()
})
</script>

<style scoped>
.page {
    min-height: 100vh;
    padding: 30px;
    background: #f5f8f6;
}

.heading {
    margin-bottom: 25px;
}

.heading h2 {
    color: #2f5d50;
}

.heading p {
    color: #777;
}

.profile-box {
    background: white;
    padding: 25px;
    border-radius: 10px;
}

.profile-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

h3 {
    color: #2f5d50;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 5px;
    cursor: pointer;
}

.details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
}

.details label {
    color: #777;
    font-weight: bold;
}

.details p {
    color: #333;
    margin-top: 8px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #444;
}

input,
textarea {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
}

textarea {
    min-height: 90px;
    resize: vertical;
}

input:disabled {
    background: #eee;
}

.buttons {
    display: flex;
    gap: 12px;
}

.cancel-btn {
    background: #777;
}

.create-message {
    margin-top: 25px;
}

.message {
    padding: 12px;
    background: #eef4f0;
    color: #2f5d50;
    margin-bottom: 15px;
    border-radius: 5px;
}

.loading {
    color: #2f5d50;
}
</style>
