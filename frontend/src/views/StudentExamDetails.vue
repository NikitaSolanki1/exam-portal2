
<template>
    <Navbar />

    <div class="student-page">

        <div class="details">

            <h2>Examination Details</h2>
            <p>View complete examination information.</p>

            <div class="details-box" v-if="exam">

                <h3>{{ exam.exam_name }}</h3>

                <div class="detail-row">
                    <strong>Exam Name</strong>
                    <span>{{ exam.exam_name }}</span>
                </div>

                <div class="detail-row">
                    <strong>Exam Type</strong>
                    <span>{{ exam.exam_type }}</span>
                </div>

                <div class="detail-row">
                    <strong>Course Name</strong>
                    <span>{{ exam.course_name }}</span>
                </div>

                <div class="detail-row">
                    <strong>Exam Start Date</strong>
                    <span>{{ exam.exam_start_date }}</span>
                </div>

                <div class="detail-row">
                    <strong>Exam End Date</strong>
                    <span>{{ exam.exam_end_date }}</span>
                </div>

                <div class="detail-row">
                    <strong>Booking Start</strong>
                    <span>{{ exam.booking_start_time }}</span>
                </div>

                <div class="detail-row">
                    <strong>Booking End</strong>
                    <span>{{ exam.booking_end_time }}</span>
                </div>

                <div class="detail-row">
                    <strong>Booking Status</strong>
                    <span :class="exam.booking_status === 'Open' ? 'open' : 'closed'">
                        {{ exam.booking_status }}
                    </span>
                </div>

                <div class="detail-row">
                    <strong>Examination Status</strong>
                    <span>{{ exam.status }}</span>
                </div>

                <button @click="router.push('/student/examination-slots/' + exam.id)">
                    View Slots
                </button>

            </div>

            <p v-else class="message">Examination details not found.</p>

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

const exam = ref(null)

const getExamDetails = async () => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.get(
            'http://127.0.0.1:5000/student/examination-details/' + route.params.id,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        exam.value = response.data

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

onMounted(() => {
    getExamDetails()
})

</script>

<style scoped>

.student-page {
    min-height: 100vh;
    background: #f5f5f5;
}

.details {
    max-width: 850px;
    margin: 35px auto;
    padding: 0 20px;
}

.details h2 {
    color: #333;
}

.details p {
    color: #666;
}

.details-box {
    background: white;
    border: 1px solid #ddd;
    padding: 25px;
    margin-top: 25px;
}

.details-box h3 {
    color: #2f5d50;
    margin-bottom: 20px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    padding: 14px 0;
    border-bottom: 1px solid #eee;
}

.detail-row strong {
    color: #444;
}

.detail-row span {
    color: #666;
}

.open {
    color: green !important;
    font-weight: bold;
}

.closed {
    color: #c0392b !important;
    font-weight: bold;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 18px;
    margin-top: 20px;
    cursor: pointer;
}

button:hover {
    background: #24483e;
}

.back-btn {
    margin-left: 10px;
}

.message {
    margin-top: 25px;
}

</style>

