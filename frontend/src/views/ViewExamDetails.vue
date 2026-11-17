
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <div>
                <h1>Examination Details</h1>
                <p>Complete examination information</p>
            </div>

            <button @click="goBack">Back</button>
        </div>

        <div v-if="message" class="message" :class="{ ok: messageOk }">
            {{ message }}
        </div>

        <div v-if="examination" class="details-card">

            <h2>{{ examination.exam_name }}</h2>

            <div class="details-grid">
                <div>
                    <label>Examination Type</label>
                    <p>{{ examination.exam_type }}</p>
                </div>

                <div>
                    <label>Course Name</label>
                    <p>{{ examination.course_name }}</p>
                </div>

                <div>
                    <label>Course Code</label>
                    <p>{{ examination.course_code }}</p>
                </div>

                <div>
                    <label>Examiner Name</label>
                    <p>{{ examination.examiner_name }}</p>
                </div>

                <div>
                    <label>Examiner Email</label>
                    <p>{{ examination.examiner_email }}</p>
                </div>

                <div>
                    <label>Status</label>
                    <p>{{ examination.status }}</p>
                </div>

                <div>
                    <label>Slot Start Date</label>
                    <p>{{ examination.slot_start_date }}</p>
                </div>

                <div>
                    <label>Slot End Date</label>
                    <p>{{ examination.slot_end_date }}</p>
                </div>

                <div>
                    <label>Booking Start</label>
                    <p>{{ examination.booking_start_time }}</p>
                </div>

                <div>
                    <label>Booking End</label>
                    <p>{{ examination.booking_end_time }}</p>
                </div>

                <div>
                    <label>Exam Start</label>
                    <p>{{ examination.exam_start_time }}</p>
                </div>

                <div>
                    <label>Exam End</label>
                    <p>{{ examination.exam_end_time }}</p>
                </div>
            </div>

            <div class="reassign-box">
                <h2>Reassign Examiner</h2>
                <p class="hint">
                    Examiners with no slots are free. Admin can assign any free examiner.
                </p>
                <form class="reassign-form" @submit.prevent="changeExaminer">
                    <select v-model="selectedExaminerId" required>
                        <option disabled value="">Select examiner</option>
                        <option
                            v-for="examiner in examiners"
                            :key="examiner.id"
                            :value="examiner.id"
                            :disabled="!examiner.is_free && examiner.id !== examination.examiner_id"
                        >
                            {{ examiner.name }}
                            {{ examinerLabel(examiner) }}
                        </option>
                    </select>
                    <button type="submit">Change examiner</button>
                </form>
            </div>

            <div class="rubric-section">
                <h2>Examination Rubrics</h2>

                <table>
                    <thead>
                        <tr>
                            <th>Criterion</th>
                            <th>Maximum Marks</th>
                            <th>Description</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="rubric in examination.rubrics"
                            :key="rubric.id">
                            <td>{{ rubric.criterion_name }}</td>
                            <td>{{ rubric.maximum_marks }}</td>
                            <td>{{ rubric.description || '-' }}</td>
                        </tr>

                        <tr v-if="examination.rubrics.length === 0">
                            <td colspan="3">No rubrics created</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="slots-section">
                <h2>Slots / Reschedule</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Start</th>
                            <th>End</th>
                            <th>Examiner</th>
                            <th>Booked by</th>
                            <th>Status</th>
                            <th>Reschedule</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="slot in examination.slots" :key="slot.id">
                            <td>
                                <input
                                    v-if="!slot.evaluated"
                                    type="date"
                                    v-model="slot.date"
                                    :min="examDateMin"
                                    :max="examDateMax"
                                >
                                <span v-else>{{ slot.date }}</span>
                            </td>
                            <td>
                                <input
                                    v-if="!slot.evaluated"
                                    type="time"
                                    v-model="slot.start_time"
                                >
                                <span v-else>{{ slot.start_time }}</span>
                            </td>
                            <td>
                                <input
                                    v-if="!slot.evaluated"
                                    type="time"
                                    v-model="slot.end_time"
                                >
                                <span v-else>{{ slot.end_time }}</span>
                            </td>
                            <td>{{ slot.examiner_name || '-' }}</td>
                            <td>{{ slot.booked_by }}</td>
                            <td>{{ slot.status }}</td>
                            <td>
                                <button
                                    v-if="!slot.evaluated"
                                    type="button"
                                    class="save-btn"
                                    @click="rescheduleSlot(slot)"
                                >
                                    Save
                                </button>
                                <span v-else>Marks given</span>
                            </td>
                        </tr>
                        <tr v-if="!examination.slots || examination.slots.length === 0">
                            <td colspan="7">No slots created</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const examination = ref(null)
const examiners = ref([])
const selectedExaminerId = ref('')
const message = ref('')
const messageOk = ref(false)

const authHeaders = () => ({
    Authorization: 'Bearer ' + localStorage.getItem('access_token')
})

const examDateMin = computed(() =>
    String(examination.value?.exam_start_time || '').slice(0, 10) || undefined
)
const examDateMax = computed(() =>
    String(examination.value?.exam_end_time || '').slice(0, 10) || undefined
)

const fetchDetails = async () => {
    try {
        const response = await axios.get(
            `http://127.0.0.1:5000/admin_exam_detail/${route.params.id}`,
            { headers: authHeaders() }
        )

        examination.value = response.data
        selectedExaminerId.value = response.data.examiner_id || ''
    } catch (error) {
        messageOk.value = false
        message.value = error.response?.data?.message || 'Unable to load examination details'
    }
}

const examinerLabel = (examiner) => {
    if (examiner.is_blocked) return '(Blocked)'
    if (examination.value && examiner.id === examination.value.examiner_id) {
        return '(Current)'
    }
    if (!examiner.has_slots) return '(Free — no slots)'
    if (examiner.is_free) return '(Free)'
    return '(Not free)'
}

const fetchExaminers = async () => {
    try {
        const response = await axios.get(
            `http://127.0.0.1:5000/admin/exam-free-examiners/${route.params.id}`,
            { headers: authHeaders() }
        )
        examiners.value = response.data.data || []
    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const changeExaminer = async () => {
    if (!selectedExaminerId.value) {
        messageOk.value = false
        message.value = 'Please select an examiner'
        return
    }

    try {
        const response = await axios.post(
            `http://127.0.0.1:5000/admin/reassign-exam-examiner/${route.params.id}`,
            { examiner_id: selectedExaminerId.value },
            { headers: authHeaders() }
        )
        messageOk.value = true
        message.value = response.data.message
        await fetchDetails()
        await fetchExaminers()
    } catch (error) {
        messageOk.value = false
        message.value = error.response?.data?.message || 'Unable to reassign examiner'
    }
}

const rescheduleSlot = async (slot) => {
    try {
        const response = await axios.post(
            `http://127.0.0.1:5000/admin/reschedule-slot/${slot.id}`,
            {
                slot_date: slot.date,
                slot_time: slot.start_time,
                end_time: slot.end_time
            },
            { headers: authHeaders() }
        )
        messageOk.value = true
        message.value = response.data.message
        await fetchDetails()
    } catch (error) {
        messageOk.value = false
        message.value = error.response?.data?.message || 'Unable to reschedule slot'
    }
}

const goBack = () => {
    router.push('/admin/examinations')
}

onMounted(async () => {
    await fetchExaminers()
    await fetchDetails()
})
</script>

<style scoped>
.page {
    padding: 30px;
    background: #f5f8f6;
    min-height: 90vh;
}

.heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.heading h1 {
    color: #2f5d50;
    margin-bottom: 5px;
}

.heading p {
    color: #666;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}

.details-card {
    background: white;
    padding: 25px;
    border-radius: 8px;
}

.details-card h2 {
    color: #2f5d50;
    margin-bottom: 25px;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
}

.details-grid label {
    color: #777;
    font-size: 14px;
}

.details-grid p {
    color: #333;
    font-weight: 500;
    margin-top: 7px;
}

.reassign-box {
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #e5e5e5;
}

.hint {
    color: #666;
    margin: -10px 0 15px;
}

.reassign-form {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}

.reassign-form select {
    min-width: 240px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

.rubric-section,
.slots-section {
    margin-top: 35px;
    overflow-x: auto;
}

.rubric-section h2,
.slots-section h2 {
    margin-bottom: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px;
}

th, td {
    padding: 13px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

th {
    background: #2f5d50;
    color: white;
}

td input {
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.save-btn {
    padding: 8px 14px;
}

.message {
    color: #b00020;
    margin-bottom: 15px;
}

.message.ok {
    color: #2f5d50;
}
</style>
