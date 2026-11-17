<template>
    <Navbar />

    <div class="page">

        <div class="heading">
            <h2>Assigned Examinations</h2>
            <p>View your assigned examinations and create examination slots</p>
        </div>

        <div class="exam-list">

            <div class="exam-card" v-for="exam in examinations" :key="exam.id">

                <div class="exam-info">
                    <h3>{{ exam.exam_name }}</h3>
                    <p><b>Course Name:</b> {{ exam.course_name }}</p>
                    <p>Exam Type: {{ exam.exam_type }}</p>
                    <p>Slot Start: {{ exam.slot_start_date }}</p>
                    <p>Slot End: {{ exam.slot_end_date }}</p>
                    <p><b>Student Booking Start:</b> {{ exam.booking_start_time }}</p>

                    <p><b>Student Booking End:</b> {{ exam.booking_end_time }}</p>
                    <p>Exam Date: {{ exam.exam_start_time }}</p>

                    <p>Exam End Date: {{ exam.exam_end_time }}</p>

                    <span v-if="exam.results_published" class="closed">
                        Exam Finished
                    </span>
                    <span v-else :class="exam.slot_creation_open ? 'open' : 'closed'">
                        {{ exam.slot_creation_open ? 'Slot Creation Open' : 'Slot Creation Closed' }}
                    </span>
                </div>

                <button v-if="!exam.results_published && exam.slot_creation_open" @click="openForm(exam)">
                    Create Slot
                </button>

                <p v-else-if="exam.results_published" class="closed-text">
                    This examination is finished. Slots are closed.
                </p>

                <p v-else class="closed-text">
                    Slot creation is currently closed
                </p>

            </div>

            <p v-if="examinations.length === 0" class="empty">
                No examinations assigned to you.
            </p>

        </div>

        <div v-if="selectedExam" class="form-box">

            <h3>Create Examination Slot</h3>

            <p>{{ selectedExam.exam_name }}</p>

            <form @submit.prevent="createSlot">

                <label>Date</label>
                <input type="date" v-model="date" :min="selectedExam.exam_start_time"
                    :max="selectedExam.exam_end_time" required>

                <label>Start Time</label>
                <input type="time" v-model="start_time" required>

                <label>End Time</label>
                <input type="time" v-model="end_time" required>

                <label>Maximum Capacity (fixed to 1 seat)</label>
                <input type="number" v-model="maximum_capacity" min="1" max="1" readonly required>

                <div class="form-buttons">
                    <button type="submit">Create Slot</button>
                    <button type="button" class="cancel" @click="closeForm">
                        Cancel
                    </button>
                </div>

            </form>

        </div>

        <div class="section">

            <h3>My Created Slots</h3>

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
                        </tr>

                        <tr v-if="slots.length === 0">
                            <td colspan="7" class="empty">
                                No slots created yet.
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>

        </div>

        <p v-if="message" class="message">{{ message }}</p>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const examinations = ref([])
const slots = ref([])

const selectedExam = ref(null)

const date = ref("")
const start_time = ref("")
const end_time = ref("")
const maximum_capacity = ref(1)

const message = ref("")

const token = localStorage.getItem("access_token")

const fetchExaminations = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/assigned-examinations",
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        examinations.value = response.data.data

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load examinations"
    }
}

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

const openForm = (exam) => {
    selectedExam.value = exam
    date.value = ""
    start_time.value = ""
    end_time.value = ""
    maximum_capacity.value = 1
    message.value = ""
}

const closeForm = () => {
    selectedExam.value = null
}

const createSlot = async () => {
    try {
        const response = await axios.post(
            "http://127.0.0.1:5000/examiner/create-slot",
            {
                examination_id: selectedExam.value.id,
                date: date.value,
                start_time: start_time.value,
                end_time: end_time.value,
                maximum_capacity: maximum_capacity.value
            },
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        )

        message.value = response.data.message

        if (String(response.data.message || "").toLowerCase().includes("created")) {
            closeForm()
            await fetchSlots()
        }

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to create slot"
    }
}

onMounted(() => {
    fetchExaminations()
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

.exam-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 25px;
}

.exam-card {
    background: white;
    padding: 22px;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

.exam-info h3 {
    color: #2f5d50;
    margin-bottom: 12px;
}

.exam-info p {
    color: #666;
    margin-bottom: 8px;
}

.open {
    display: inline-block;
    background: #e2f3e8;
    color: #267344;
    padding: 6px 10px;
    border-radius: 5px;
    margin-top: 8px;
}

.closed {
    display: inline-block;
    background: #fff1d6;
    color: #946200;
    padding: 6px 10px;
    border-radius: 5px;
    margin-top: 8px;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    cursor: pointer;
}

.closed-text {
    color: #946200;
}

.form-box,
.section {
    background: white;
    padding: 25px;
    border-radius: 10px;
    margin-bottom: 25px;
}

.form-box h3,
.section h3 {
    color: #2f5d50;
    margin-bottom: 15px;
}

.form-box form {
    max-width: 500px;
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

.table-box {
    width: 100%;
    overflow-x: auto;
}

table {
    width: 100%;
    min-width: 750px;
    border-collapse: collapse;
}

th,
td {
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
