
<template>
    <Navbar />

    <div class="student-page">

        <div class="slots">

            <h2>Examination Slots</h2>
            <p>View and book examination slots.</p>

            <div class="exam-heading" v-if="examName">
                <h3>{{ examName }}</h3>

                <p>Course Name: {{ courseName }}</p>

                <p>
                    Booking Status:
                    <strong :class="bookingOpen ? 'open' : 'closed'">
                        {{ bookingOpen ? 'Open' : 'Closed' }}
                    </strong>
                </p>
            </div>

            <p class="message" v-if="message">
                {{ message }}
            </p>

            <div class="table-box">

                <table>
                    <thead>
                        <tr>
                            <th>Slot Date</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Maximum Capacity</th>
                            <th>Available Seats</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="slot in slots" :key="slot.id">

                            <td>{{ slot.date }}</td>
                            <td>{{ slot.start_time }}</td>
                            <td>{{ slot.end_time }}</td>
                            <td>{{ slot.maximum_capacity }}</td>
                            <td>{{ slot.available_seats }}</td>

                            <td>
                                <span :class="slot.status.toLowerCase()">
                                    {{ slot.status }}
                                </span>
                            </td>

                            <td>
                                <button
                                    @click="bookSlot(slot.id)"
                                    :disabled="!bookingOpen || slot.available_seats <= 0 || slot.status !== 'Available' || slot.date < today"
                                >
                                    Book Slot
                                </button>
                            </td>

                        </tr>

                        <tr v-if="slots.length === 0">
                            <td colspan="7" class="empty">
                                No Examination Slots Found
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>

            <button class="back-btn" @click="router.push('/student/examination')">
                Back to Examinations
            </button>

        </div>
    </div>
</template>

<script setup>

import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()

const slots = ref([])
const examName = ref("")
const courseName = ref("")
const bookingOpen = ref(false)
const message = ref("")

const today = new Date().toISOString().split("T")[0]

const getSlots = async () => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.get(
            'http://127.0.0.1:5000/student/examination-slots/' + route.params.id,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        slots.value = response.data.data
        examName.value = response.data.exam_name
        courseName.value = response.data.course_name
        bookingOpen.value = response.data.booking_open

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const bookSlot = async (slotId) => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.post(
            'http://127.0.0.1:5000/student/book-slot',
            {
                slot_id: slotId
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        await getSlots()

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to book slot"
    }
}

onMounted(() => {
    getSlots()
})

</script>

<style scoped>

.student-page {
    min-height: 100vh;
    background: #f5f5f5;
}

.slots {
    max-width: 1100px;
    margin: 35px auto;
    padding: 0 20px;
}

.slots h2 {
    color: #333;
}

.slots p {
    color: #666;
}

.exam-heading {
    background: white;
    border: 1px solid #ddd;
    padding: 15px 20px;
    margin: 25px 0;
}

.exam-heading h3 {
    color: #2f5d50;
    margin-top: 0;
}

.open {
    color: green;
}

.closed {
    color: #c0392b;
}

.table-box {
    background: white;
    border: 1px solid #ddd;
    padding: 15px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #2f5d50;
    color: white;
}

.available {
    color: green;
    font-weight: bold;
}

.full {
    color: #c0392b;
    font-weight: bold;
}

.empty {
    text-align: center;
    color: #666;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 9px 13px;
    cursor: pointer;
}

button:hover {
    background: #24483e;
}

button:disabled {
    background: #999;
    cursor: not-allowed;
}

.back-btn {
    margin-top: 20px;
}

.message {
    background: white;
    padding: 12px;
    border: 1px solid #ddd;
    color: #2f5d50;
}

</style>
