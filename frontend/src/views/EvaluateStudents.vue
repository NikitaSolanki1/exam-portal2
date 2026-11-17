
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <h2>Evaluate Students</h2>
            <p>View booked students and submit their examination marks</p>
        </div>

        <div v-if="message" class="message">
            {{ message }}
        </div>

        <div v-if="!selectedBooking" class="table-box">
            <h3>Pending Evaluations</h3>

            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Email</th>
                        <th>Examination</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="student in students" :key="student.booking_id">
                        <td>{{ student.student_name }}</td>
                        <td>{{ student.student_email }}</td>
                        <td>{{ student.exam_name }}</td>
                        <td>{{ student.date }}</td>
                        <td>
                            <button @click="openEvaluation(student.booking_id)">
                                Evaluate
                            </button>
                        </td>
                    </tr>

                    <tr v-if="students.length === 0">
                        <td colspan="5">No pending evaluations found</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="selectedBooking" class="form-box">
            <button class="back-btn" @click="closeEvaluation">
                Back to Students
            </button>

            <h3>Student Evaluation</h3>

            <p><b>Student:</b> {{ studentDetails.student_name }}</p>
            <p><b>Email:</b> {{ studentDetails.student_email }}</p>
            <p><b>Examination:</b> {{ studentDetails.exam_name }}</p>

            <h3>Evaluation Criteria</h3>

            <div v-for="rubric in rubrics" :key="rubric.id" class="rubric">
                <label>{{ rubric.criterion_name }}</label>

                <p>{{ rubric.description }}</p>

                <p>Maximum Marks: {{ rubric.maximum_marks }}</p>

                <input
                    type="number"
                    v-model="rubric.marks"
                    min="0"
                    :max="rubric.maximum_marks"
                    placeholder="Enter marks"
                />
            </div>

            <div class="remarks">
                <label>Remarks</label>
                <textarea
                    v-model="remarks"
                    placeholder="Enter your remarks"
                ></textarea>
            </div>

            <h3>Total Marks: {{ totalMarks }}</h3>

            <button @click="submitEvaluation" :disabled="loading">
                {{ loading ? "Submitting..." : "Submit Evaluation" }}
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const students = ref([])
const selectedBooking = ref(null)
const studentDetails = ref({})
const rubrics = ref([])
const remarks = ref("")
const message = ref("")
const loading = ref(false)

const token = localStorage.getItem("access_token")

const headers = {
    Authorization: `Bearer ${token}`
}

const totalMarks = computed(() => {
    return rubrics.value.reduce((total, rubric) => {
        return total + (Number(rubric.marks) || 0)
    }, 0)
})

const getStudents = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/evaluations",
            { headers }
        )

        students.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load students"
    }
}

const openEvaluation = async (bookingId) => {
    message.value = ""

    try {
        const response = await axios.get(
            `http://127.0.0.1:5000/examiner/evaluation-details/${bookingId}`,
            { headers }
        )

        selectedBooking.value = bookingId
        studentDetails.value = response.data
        rubrics.value = response.data.rubrics.map(rubric => ({
            ...rubric,
            marks: ""
        }))

        remarks.value = ""

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load evaluation details"
    }
}

const closeEvaluation = () => {
    selectedBooking.value = null
    studentDetails.value = {}
    rubrics.value = []
    remarks.value = ""
    message.value = ""
}

const submitEvaluation = async () => {
    if (rubrics.value.length === 0) {
        message.value = "No evaluation criteria found"
        return
    }

    for (const rubric of rubrics.value) {
        if (
            rubric.marks === "" ||
            Number(rubric.marks) < 0 ||
            Number(rubric.marks) > rubric.maximum_marks
        ) {
            message.value = `Enter valid marks for ${rubric.criterion_name}`
            return
        }
    }

    loading.value = true

    try {
        const response = await axios.post(
            `http://127.0.0.1:5000/examiner/submit-evaluation/${selectedBooking.value}`,
            {
                marks: rubrics.value.map(rubric => ({
                    rubric_id: rubric.id,
                    marks: Number(rubric.marks)
                })),
                remarks: remarks.value
            },
            { headers }
        )

        message.value = response.data.message

        selectedBooking.value = null
        await getStudents()

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to submit evaluation"
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    getStudents()
})
</script>

<style scoped>
.page {
    padding: 30px;
    background: #f5f8f6;
    min-height: 90vh;
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
.form-box {
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

button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.back-btn {
    margin-bottom: 20px;
}

.rubric {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 7px;
    margin: 15px 0;
}

.rubric label,
.remarks label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

.rubric p {
    color: #666;
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
    min-height: 90px;
    resize: vertical;
}

.remarks {
    margin: 20px 0;
}

.message {
    padding: 12px;
    background: #eef4f0;
    color: #2f5d50;
    border-radius: 5px;
    margin-bottom: 15px;
}
</style>
