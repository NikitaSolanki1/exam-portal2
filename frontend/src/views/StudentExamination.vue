<template>
    <Navbar />

    <div class="student-page">
        <div class="examination">

            <h2>See Examination</h2>
            <p>Search and view examinations.</p>

            <div class="filters">
                <input type="text" v-model="search" placeholder="Search Examination">

                <select v-model="selectedCourse">
                    <option value="">All Courses</option>
                    <option v-for="course in courses" :key="course.id" :value="course.course_name">
                        {{ course.course_name }}
                    </option>
                </select>
            </div>

            <div class="table-box">
                <table>
                    <thead>
                        <tr>
                            <th>Exam Name</th>
                            <th>Course Name</th>
                            <th>Exam From</th>
                            <th>Exam To</th>
                            <th>Booking</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="exam in filteredExaminations" :key="exam.id">
                            <td>{{ exam.exam_name }}</td>
                            <td>{{ exam.course_name }}</td>
                            <td>{{ exam.exam_start_date }}</td>
                            <td>{{ exam.exam_end_date }}</td>

                            <td>
                                <span :class="exam.booking_status === 'Open' ? 'open' : 'closed'">
                                    {{ exam.booking_status }}
                                </span>
                            </td>

                            <td>
                                <span :class="{
                                    'open': exam.booking_status === 'Booking Started',
                                    'closed': exam.booking_status === 'Booking Closed',
                                    'completed': exam.booking_status === 'Exam Complete'
                                }">
                                    {{ exam.booking_status }}
                                </span>
                            </td>

                            <td class="actions">
                                <button @click="viewDetails(exam.id)">
                                    View Details
                                </button>

                                <button @click="viewSlots(exam.id)">
                                    View Slot
                                </button>
                            </td>
                        </tr>

                        <tr v-if="filteredExaminations.length === 0">
                            <td colspan="7" class="empty">
                                No Examinations Found
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
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'

const router = useRouter()

const examinations = ref([])
const courses = ref([])

const search = ref("")
const selectedCourse = ref("")

const getExaminations = async () => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.get(
            'http://127.0.0.1:5000/student/examinations',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        examinations.value = response.data.data || []
        courses.value = response.data.courses || []

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const filteredExaminations = computed(() => {
    return examinations.value.filter((exam) => {

        const examName = (exam.exam_name || "").toLowerCase()
        const courseName = (exam.course_name || "").toLowerCase()
        const searchText = search.value.toLowerCase()

        const searchMatch =
            examName.includes(searchText) ||
            courseName.includes(searchText)

        const courseMatch =
            selectedCourse.value === "" ||
            exam.course_name === selectedCourse.value

        return searchMatch && courseMatch
    })
})

const viewDetails = (id) => {
    router.push('/student/examination-details/' + id)
}

const viewSlots = (id) => {
    router.push('/student/examination-slots/' + id)
}

onMounted(() => {
    getExaminations()
})
</script>

<style scoped>
.student-page {
    min-height: 100vh;
    background: #f5f5f5;
}

.examination {
    max-width: 1100px;
    margin: 35px auto;
    padding: 0 20px;
}

.examination h2 {
    color: #333;
}

.examination p {
    color: #666;
}

.filters {
    display: flex;
    gap: 15px;
    margin: 25px 0;
}

.filters input,
.filters select {
    padding: 10px;
    width: 250px;
    border: 1px solid #ddd;
    background: white;
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

.open {
    color: green;
    font-weight: bold;
}

.closed {
    color: #c0392b;
    font-weight: bold;
}

.upcoming {
    color: #b7791f;
    font-weight: bold;
}

.active {
    color: green;
    font-weight: bold;
}

.completed {
    color: #666;
    font-weight: bold;
}

.actions {
    display: flex;
    gap: 8px;
}

.actions button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 8px 10px;
    cursor: pointer;
}

.actions button:hover {
    background: #24483e;
}

.empty {
    text-align: center;
    color: #666;
}
</style>
