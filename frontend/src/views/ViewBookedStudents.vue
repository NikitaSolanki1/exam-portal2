
<template>
    <Navbar />

    <div class="page">

        <div class="heading">
            <h2>Booked Students</h2>
            <p>View students booked in your examination slots</p>
        </div>

        <div class="table-box">

            <table>
                <thead>
                    <tr>
                        <th>Student Name</th>
                        <th>Email</th>
                        <th>Examination</th>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Booking Status</th>
                        <th>Evaluation Status</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="student in students" :key="student.booking_id">
                        <td>{{ student.student_name }}</td>
                        <td>{{ student.student_email }}</td>
                        <td>{{ student.exam_name }}</td>
                        <td>{{ student.date }}</td>
                        <td>{{ student.start_time }}</td>
                        <td>{{ student.end_time }}</td>
                        <td>{{ student.booking_status }}</td>
                        <td>{{ student.evaluation_status }}</td>
                    </tr>

                    <tr v-if="students.length === 0">
                        <td colspan="8" class="empty">
                            No students have booked your slots yet.
                        </td>
                    </tr>
                </tbody>
            </table>

        </div>

        <p v-if="message" class="message">{{ message }}</p>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const students = ref([])
const message = ref("")

const token = localStorage.getItem("access_token")

const fetchStudents = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/booked-students",
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        students.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load students"
    }
}

onMounted(() => {
    fetchStudents()
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
    min-width: 1000px;
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

.empty {
    text-align: center;
    color: #777;
}

.message {
    margin-top: 15px;
    color: #2f5d50;
}
</style>
