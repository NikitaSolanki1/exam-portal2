<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <h2>Submitted Evaluations</h2>
            <p>View your completed student evaluations</p>
        </div>

        <div v-if="message" class="message">
            {{ message }}
        </div>

        <div v-if="!selectedEvaluation" class="table-box">
            <h3>Evaluation History</h3>

            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Email</th>
                        <th>Examination</th>
                        <th>Total Marks</th>
                        <th>Evaluation Date</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="evaluation in evaluations" :key="evaluation.id">
                        <td>{{ evaluation.student_name }}</td>
                        <td>{{ evaluation.student_email }}</td>
                        <td>{{ evaluation.exam_name }}</td>
                        <td>{{ evaluation.total_marks }}</td>
                        <td>{{ evaluation.date }}</td>
                        <td>
                            <button @click="viewDetails(evaluation.id)">
                                View Details
                            </button>
                        </td>
                    </tr>

                    <tr v-if="evaluations.length === 0">
                        <td colspan="6">No submitted evaluations found</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="selectedEvaluation" class="details-box">
            <button class="back-btn" @click="selectedEvaluation = null">
                Back to Evaluations
            </button>

            <h3>Evaluation Details</h3>

            <p><b>Student:</b> {{ selectedEvaluation.student_name }}</p>
            <p><b>Email:</b> {{ selectedEvaluation.student_email }}</p>
            <p><b>Examination:</b> {{ selectedEvaluation.exam_name }}</p>
            <p><b>Evaluation Date:</b> {{ selectedEvaluation.evaluation_date }}</p>

            <h3>Rubric Marks</h3>

            <table>
                <thead>
                    <tr>
                        <th>Criteria</th>
                        <th>Maximum Marks</th>
                        <th>Marks Obtained</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="rubric in selectedEvaluation.rubrics" :key="rubric.criterion_name">
                        <td>{{ rubric.criterion_name }}</td>
                        <td>{{ rubric.maximum_marks }}</td>
                        <td>{{ rubric.marks_obtained }}</td>
                    </tr>
                </tbody>
            </table>

            <div class="total">
                Total Marks: {{ selectedEvaluation.total_marks }}
            </div>

            <div class="remarks">
                <h3>Examiner Remarks</h3>
                <p>{{ selectedEvaluation.remarks || "No remarks added" }}</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const evaluations = ref([])
const selectedEvaluation = ref(null)
const message = ref("")

const token = localStorage.getItem("access_token")

const headers = {
    Authorization: `Bearer ${token}`
}

const getEvaluations = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/submitted-evaluations",
            { headers }
        )

        evaluations.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message ||
            "Unable to load submitted evaluations"
    }
}

const viewDetails = async (evaluationId) => {
    message.value = ""

    try {
        const response = await axios.get(
            `http://127.0.0.1:5000/examiner/submitted-evaluation-details/${evaluationId}`,
            { headers }
        )

        selectedEvaluation.value = response.data

    } catch (error) {
        message.value = error.response?.data?.message ||
            "Unable to load evaluation details"
    }
}

onMounted(() => {
    getEvaluations()
})
</script>

<style scoped>
.page {
    padding: 30px;
    min-height: 90vh;
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

.table-box,
.details-box {
    background: white;
    padding: 25px;
    border-radius: 10px;
    margin-top: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th,
td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #eef4f0;
    color: #2f5d50;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 5px;
    cursor: pointer;
}

.back-btn {
    margin-bottom: 20px;
}

.total {
    margin-top: 20px;
    font-size: 18px;
    font-weight: bold;
    color: #2f5d50;
}

.remarks {
    margin-top: 25px;
    padding: 15px;
    background: #f5f8f6;
    border-radius: 7px;
}

.message {
    padding: 12px;
    background: #eef4f0;
    color: #2f5d50;
    border-radius: 5px;
    margin-bottom: 15px;
}
</style>
