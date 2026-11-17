
<template>
    <Navbar />

    <div class="student-page">
        <div class="bookings">

            <h2>My Bookings</h2>
            <p>View your examination bookings.</p>

            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>Exam Name</th>
                            <th>Course Name</th>
                            <th>Exam Type</th>
                            <th>Slot Date</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Booking Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="booking in bookings" :key="booking.booking_id">
                            <td>{{ booking.exam_name }}</td>
                            <td>{{ booking.course_name }}</td>
                            <td>{{ booking.exam_type }}</td>
                            <td>{{ booking.slot_date }}</td>
                            <td>{{ booking.start_time }}</td>
                            <td>{{ booking.end_time }}</td>
                            <td>{{ booking.booking_date }}</td>

                            <td>
                                <span :class="booking.booking_status.toLowerCase()">
                                    {{ booking.booking_status }}
                                </span>
                            </td>
                        </tr>

                        <tr v-if="bookings.length === 0">
                            <td colspan="8" class="empty">
                                No Bookings Found
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref, onMounted } from 'vue'

const bookings = ref([])

const getBookings = async () => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.get(
            'http://127.0.0.1:5000/student/my-bookings',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        bookings.value = response.data.data || []

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

onMounted(() => {
    getBookings()
})
</script>

<style scoped>
.student-page {
    min-height: 100vh;
    background: #f5f5f5;
}

.bookings {
    max-width: 1200px;
    margin: 35px auto;
    padding: 0 20px;
}

.bookings h2 {
    color: #333;
}

.bookings p {
    color: #666;
}

.table-box {
    background: white;
    border: 1px solid #ddd;
    padding: 15px;
    margin-top: 25px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #2f5d50;
    color: white;
}

.booked {
    color: green;
    font-weight: bold;
}

.completed {
    color: #2f5d50;
    font-weight: bold;
}

.cancelled {
    color: #c0392b;
    font-weight: bold;
}

.empty {
    text-align: center;
    color: #666;
}
</style>
