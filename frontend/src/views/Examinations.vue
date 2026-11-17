
<template>
    <Navbar />

    <div class="page">
        <div class="content">

            <div class="page-heading">
                <div>
                    <h2>Manage Examination</h2>
                    <p>Manage assigned examinations</p>
                </div>

                <button class="create-btn" @click="router.push('/admin/createexamination')">
                    Create Examination
                </button>
            </div>

            <div class="table-box">

                <div class="search-box">
                    <input v-model="search" type="text" placeholder="Search examination...">
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Slot Creation Start</th>
                            <th>Slot Creation End</th>
                            <th>Booking Start</th>
                            <th>Booking End</th>
                            <th>Status</th>
                            <th>Rubric</th>
                            <th>Slot Creation</th>
                            <th>Student Booking</th>
                            <th>Details</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="examination in filteredExaminations" :key="examination.id">

                            <td>{{ examination.name }}</td>
                            <td>{{ examination.slot_start_date }}</td>
                            <td>{{ examination.slot_end_date }}</td>
                            <td>{{ examination.booking_start_time }}</td>
                            <td>{{ examination.booking_end_time }}</td>

                            <td>
                                <span :class="examination.results_published ? 'finished' : 'active-status'">
                                    {{ examination.results_published ? 'Finished' : (examination.status || 'Active') }}
                                </span>
                            </td>

                            <td>
                                <button class="action-btn" @click="create_rubric(examination.id)">
                                    Create
                                </button>

                                <button class="action-btn" @click="manage_rubric(examination.id)">
                                    Manage
                                </button>
                            </td>

                            <td>
                                <template v-if="examination.results_published">
                                    <span class="finished">Finished</span>
                                </template>
                                <button
                                    v-else
                                    class="action-btn"
                                    @click="toggle_slot(examination)"
                                >
                                    {{ examination.slot_open ? 'Close Slot' : 'Open Slot' }}
                                </button>
                            </td>

                            <td>
                                <template v-if="examination.results_published">
                                    <span class="finished">Finished</span>
                                </template>
                                <button
                                    v-else
                                    class="action-btn"
                                    @click="toggle_booking(examination)"
                                >
                                    {{ examination.booking_open ? 'Close Booking' : 'Open Booking' }}
                                </button>
                            </td>

                            <td>
                                <button class="action-btn" @click="view_slot(examination.id)">
                                    View Slot
                                </button>

                                <button class="action-btn" @click="view_detail(examination.id)">
                                    View Detail
                                </button>

                                <button
                                    v-if="!examination.results_published"
                                    class="action-btn"
                                    @click="editExamination(examination)"
                                >
                                    Edit
                                </button>

                                <button
                                    class="action-btn"
                                    @click="publishResult(examination)"
                                    :disabled="examination.results_published"
                                >
                                    {{ examination.results_published ? 'Published' : 'Publish Result' }}
                                </button>
                            </td>
                        </tr>

                        <tr v-if="filteredExaminations.length === 0">
                            <td colspan="10" class="no-data">
                                No examinations found
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-box edit-box" v-if="selectedExam">

                <h3>Edit Examination</h3>

                <label>Examination Name</label>
                <input v-model="selectedExam.exam_name" type="text">

                <label>Examination Type</label>
                <input v-model="selectedExam.exam_type" type="text">

                <label>Slot Creation Start</label>
                <input v-model="selectedExam.slot_start_date" type="date">

                <label>Slot Creation End</label>
                <input v-model="selectedExam.slot_end_date" type="date">

                <label>Booking Start</label>
                <input v-model="selectedExam.booking_start_time" type="datetime-local">

                <label>Booking End</label>
                <input v-model="selectedExam.booking_end_time" type="datetime-local">

                <label>Exam Start Date</label>
                <input v-model="selectedExam.exam_start_time" type="date">

                <label>Exam End Date</label>
                <input v-model="selectedExam.exam_end_time" type="date">

                <button class="action-btn" @click="saveExamination">
                    Save Changes
                </button>

                <button class="action-btn cancel-btn" @click="selectedExam = null">
                    Cancel
                </button>

            </div>

            <p class="message">{{ message }}</p>

        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const response_frontend = ref([])
const search = ref('')
const message = ref('')
const selectedExam = ref(null)

const filteredExaminations = computed(() => {
    return response_frontend.value.filter(examination =>
        examination.name?.toLowerCase().includes(search.value.toLowerCase())
    )
})

const fetchExaminationDetails = async () => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(
            'http://127.0.0.1:5000/provide_examination_details',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        response_frontend.value = response.data.data

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const create_rubric = (examination_id) => {
    router.push(`/create-rubric/${examination_id}`)
}

const manage_rubric = (examination_id) => {
    router.push(`/manage-rubric/${examination_id}`)
}

const view_slot = (examination_id) => {
    router.push(`/view_slot/${examination_id}`)
}

const view_detail = (examination_id) => {
    router.push(`/admin_exam_detail/${examination_id}`)
}

const toggle_slot = async (examination) => {
    try {
        const token = localStorage.getItem('access_token')

        const path = examination.slot_open ? 'close_slot' : 'open_slot'

        await axios.post(
            `http://127.0.0.1:5000/${path}/${examination.id}`,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        await fetchExaminationDetails()

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const toggle_booking = async (examination) => {
    try {
        const token = localStorage.getItem('access_token')

        const path = examination.booking_open ? 'close_booking' : 'open_booking'

        await axios.post(
            `http://127.0.0.1:5000/${path}/${examination.id}`,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        await fetchExaminationDetails()

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const editExamination = (examination) => {
    selectedExam.value = { ...examination }
}

const saveExamination = async () => {
    try {
        const token = localStorage.getItem('access_token')

        await axios.put(
            'http://127.0.0.1:5000/admin/edit-examination/' + selectedExam.value.id,
            selectedExam.value,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        selectedExam.value = null
        await fetchExaminationDetails()

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}
const publishResult = async (examination) => {
    try {
        message.value = ''

        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            'http://127.0.0.1:5000/admin/publish-result/' + examination.id,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        await fetchExaminationDetails()

    } catch (error) {
        message.value = error.response?.data?.message || 'Something went wrong'
    }
}

onMounted(() => {
    fetchExaminationDetails()
})
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.page {
    min-height: 100vh;
    background: #f5f7f5;
    font-family: Arial, sans-serif;
}

.content {
    padding: 30px 35px;
}

.page-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.page-heading h2 {
    margin: 0 0 7px;
    color: #263b32;
}

.page-heading p {
    margin: 0;
    color: #777;
}

.create-btn {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 11px 18px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

.create-btn:hover,
.action-btn:hover {
    background: #24483d;
}

.table-box {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 20px;
    overflow-x: auto;
}

.search-box {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.search-box input {
    width: 55%;
    padding: 11px 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    outline: none;
}

.search-box input:focus {
    border-color: #2f5d50;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background: #edf2ef;
    color: #344b40;
    text-align: left;
    padding: 13px;
    font-size: 14px;
}

td {
    padding: 13px;
    border-bottom: 1px solid #eee;
    color: #555;
    font-size: 14px;
}

.action-btn {
    display: block;
    background: #2f5d50;
    color: white;
    border: none;
    padding: 8px 12px;
    margin: 5px 0;
    border-radius: 4px;
    cursor: pointer;
}

.action-btn:disabled {
    background: #888;
    cursor: not-allowed;
}

.cancel-btn {
    background: #777;
}

.no-data {
    text-align: center;
    padding: 25px;
    color: #888;
}

.message {
    text-align: center;
    color: #2f5d50;
    margin-top: 15px;
}

.edit-box {
    margin-top: 25px;
}

.edit-box h3 {
    color: #2f5d50;
    margin-bottom: 20px;
}

.edit-box label {
    display: block;
    color: #444;
    margin-top: 12px;
}

.edit-box input {
    width: 100%;
    padding: 10px;
    margin-top: 7px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.finished {
    color: #2f5d50;
    font-weight: 600;
}

.active-status {
    color: #555;
}
</style>
