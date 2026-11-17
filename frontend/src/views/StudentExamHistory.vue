
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <h2>Exam History</h2>
            <p>View your booked examinations and results</p>
        </div>

        <router-link to="/student/dashboard" class="back-btn">
            Back to Dashboard
        </router-link>

        <div class="table-box">
            <h3>My Examinations</h3>

            <p v-if="message" class="message">{{ message }}</p>

            <table>
                <thead>
                    <tr>
                        <th>Examination</th>
                        <th>Course</th>
                        <th>Exam Date</th>
                        <th>Time</th>
                        <th>Booking Status</th>
                        <th>Result</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="exam in examinations" :key="exam.booking_id">
                        <td>{{ exam.exam_name }}</td>
                        <td>{{ exam.course_name }}</td>
                        <td>{{ exam.date }}</td>
                        <td>{{ exam.start_time }}</td>
                        <td>{{ exam.booking_status }}</td>
                        <td>
                            <router-link
                                v-if="exam.result_available"
                                to="/student/results"
                                class="result-btn"
                            >
                                See Results
                            </router-link>

                            <span v-else>Not Published</span>
                        </td>
                    </tr>

                    <tr v-if="examinations.length === 0">
                        <td colspan="6">No examination history found</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const examinations = ref([])
const message = ref("")

const headers = {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
}

const getExamHistory = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/student/exam-history",
            { headers }
        )

        examinations.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message ||
            "Unable to load exam history"
    }
}

onMounted(() => {
    getExamHistory()
})
</script>

<style scoped>
.page {
    padding: 25px;
    min-height: 100vh;
    background: #f5f8f6;
}

.heading {
    margin-bottom: 25px;
}

.heading h2 {
    color: #2f5d50;
}

.heading p {
    color: #666;
}

.table-box {
    background: white;
    padding: 22px;
    border-radius: 8px;
    margin-top: 25px;
}

.table-box h3 {
    color: #2f5d50;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #eef4f0;
    color: #2f5d50;
}

.back-btn, .result-btn {
    display: inline-block;
    background: #2f5d50;
    color: white;
    padding: 10px 16px;
    border-radius: 5px;
    text-decoration: none;
}

.message {
    color: #2f5d50;
}
</style>

