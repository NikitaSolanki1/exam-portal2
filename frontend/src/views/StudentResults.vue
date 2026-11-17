
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <h2>See Results</h2>
            <p>View your published examination results</p>
        </div>

        <router-link to="/student/dashboard" class="back-btn">
            Back to Dashboard
        </router-link>

        <p v-if="message" class="message">{{ message }}</p>

        <div
            v-for="result in results"
            :key="result.evaluation_id"
            class="result-box"
        >
            <h3>{{ result.exam_name }}</h3>

            <p><b>Course:</b> {{ result.course_name }}</p>
            <p><b>Exam Date:</b> {{ result.exam_date }}</p>
            <p><b>Evaluation Date:</b> {{ result.evaluation_date }}</p>

            <h4>Marks Details</h4>

            <table>
                <thead>
                    <tr>
                        <th>Criteria</th>
                        <th>Maximum Marks</th>
                        <th>Marks Obtained</th>
                    </tr>
                </thead>

                <tbody>
                    <tr
                        v-for="rubric in result.rubrics"
                        :key="rubric.criterion_name"
                    >
                        <td>{{ rubric.criterion_name }}</td>
                        <td>{{ rubric.maximum_marks }}</td>
                        <td>{{ rubric.marks_obtained }}</td>
                    </tr>

                    <tr v-if="result.rubrics.length === 0">
                        <td colspan="3">No marks details available</td>
                    </tr>
                </tbody>
            </table>

            <div class="total">
                Total Marks: {{ result.total_marks }}
            </div>

            <div class="remarks">
                <h4>Examiner Remarks</h4>
                <p>{{ result.remarks || "No remarks added" }}</p>
            </div>
        </div>

        <div v-if="results.length === 0 && !message" class="result-box">
            No published results available.
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const results = ref([])
const message = ref("")

const headers = {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
}

const getResults = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/student/results",
            { headers }
        )

        results.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message ||
            "Unable to load results"
    }
}

onMounted(() => {
    getResults()
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

.result-box {
    background: white;
    padding: 22px;
    border-radius: 8px;
    margin-top: 25px;
    border: 1px solid #e5ebe7;
}

.result-box h3,
.result-box h4 {
    color: #2f5d50;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #eef4f0;
    color: #2f5d50;
}

.back-btn {
    display: inline-block;
    background: #2f5d50;
    color: white;
    padding: 10px 16px;
    border-radius: 5px;
    text-decoration: none;
}

.total {
    margin-top: 20px;
    font-size: 18px;
    font-weight: bold;
    color: #2f5d50;
}

.remarks {
    background: #f5f8f6;
    padding: 15px;
    margin-top: 20px;
    border-radius: 6px;
}

.message {
    color: #2f5d50;
}
</style>

