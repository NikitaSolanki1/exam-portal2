
<template>
    <Navbar />

    <div class="page">

        <div class="heading">
            <h2>Manage Slots</h2>
            <p>View, update and delete your examination slots</p>
        </div>

        <div class="table-box">

            <table>
                <thead>
                    <tr>
                        <th>Examination</th>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Capacity</th>
                        <th>Available Seats</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="slot in slots" :key="slot.id">
                        <td>{{ slot.exam_name }}</td>
                        <td>{{ slot.date }}</td>
                        <td>{{ slot.start_time }}</td>
                        <td>{{ slot.end_time }}</td>
                        <td>{{ slot.maximum_capacity }}</td>
                        <td>{{ slot.available_seats }}</td>
                        <td>{{ slot.status }}</td>

                        <td>
                            <template v-if="!slot.booking_open">
                                <button @click="openEditForm(slot)">
                                    Edit
                                </button>

                                <button class="delete" @click="deleteSlot(slot.id)">
                                    Delete
                                </button>
                            </template>

                            <span v-else>Booking Started</span>
                        </td>
                    </tr>

                    <tr v-if="slots.length === 0">
                        <td colspan="8" class="empty">
                            No slots created yet.
                        </td>
                    </tr>
                </tbody>
            </table>

        </div>

        <div v-if="selectedSlot" class="form-box">

            <h3>Update Examination Slot</h3>

            <form @submit.prevent="updateSlot">

                <label>Date</label>
                <input type="date" v-model="edit_date" required>

                <label>Start Time</label>
                <input type="time" v-model="edit_start_time" required>

                <label>End Time</label>
                <input type="time" v-model="edit_end_time" required>

                <label>Maximum Capacity (fixed to 1 seat)</label>
                <input type="number" min="1" max="1" v-model="edit_capacity" readonly required>

                <div class="form-buttons">
                    <button type="submit">Update Slot</button>

                    <button type="button" class="cancel" @click="selectedSlot = null">
                        Cancel
                    </button>
                </div>

            </form>

        </div>

        <p v-if="message" class="message">{{ message }}</p>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const slots = ref([])
const selectedSlot = ref(null)
const message = ref("")

const edit_date = ref("")
const edit_start_time = ref("")
const edit_end_time = ref("")
const edit_capacity = ref("")

const token = localStorage.getItem("access_token")

const fetchSlots = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/my-slots",
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        slots.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load slots"
    }
}

const openEditForm = (slot) => {
    selectedSlot.value = slot

    edit_date.value = slot.date
    edit_start_time.value = slot.start_time
    edit_end_time.value = slot.end_time
    edit_capacity.value = 1

    message.value = ""
}

const updateSlot = async () => {
    try {
        const response = await axios.put(
            `http://127.0.0.1:5000/examiner/update-slot/${selectedSlot.value.id}`,
            {
                date: edit_date.value,
                start_time: edit_start_time.value,
                end_time: edit_end_time.value,
                maximum_capacity: edit_capacity.value
            },
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === "Slot updated successfully") {
            selectedSlot.value = null
            await fetchSlots()
        }

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to update slot"
    }
}
const deleteSlot = async (slotId) => {
    try {
        const response = await axios.delete(
            `http://127.0.0.1:5000/examiner/delete-slot/${slotId}`,
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === "Slot deleted successfully") {
            await fetchSlots()
        }

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to delete slot"
    }
}

onMounted(() => {
    fetchSlots()
})
</script>

<style scoped>
.page {
    min-height: 100vh;
    background: #f5f8f6;
    padding: 30px;
}

.heading {
    margin-bottom: 25px;
}

.heading h2 {
    color: #2f5d50;
    margin-bottom: 7px;
}

.heading p {
    color: #777;
}

.table-box {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 100%;
    overflow-x: auto;
}

table {
    width: 100%;
    min-width: 950px;
    border-collapse: collapse;
}

th, td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #2f5d50;
    color: white;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 9px 13px;
    border-radius: 5px;
    cursor: pointer;
}

.delete {
    background: #b94a48;
    margin-left: 5px;
}

.form-box {
    background: white;
    padding: 25px;
    border-radius: 10px;
    margin-top: 25px;
    max-width: 550px;
}

.form-box h3 {
    color: #2f5d50;
    margin-bottom: 15px;
}

label {
    display: block;
    margin: 15px 0 7px;
    font-weight: 600;
}

input {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 6px;
}

.form-buttons {
    display: flex;
    gap: 12px;
    margin-top: 20px;
}

.cancel {
    background: #777;
}

.empty {
    text-align: center;
    color: #777;
}

.message {
    margin-top: 15px;
    color: #2f5d50;
}
</style>
