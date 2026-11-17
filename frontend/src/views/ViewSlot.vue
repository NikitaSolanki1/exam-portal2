
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <div>
                <h1>Examination Slots</h1>
                <p>{{ examinationName }}</p>
            </div>

            <button @click="goBack">Back</button>
        </div>

        <div v-if="message" class="message" :class="{ ok: messageOk }">
            {{ message }}
        </div>

        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Examiner</th>
                        <th>Total Seats</th>
                        <th>Available Seats</th>
                        <th>Booked Seats</th>
                        <th>Status</th>
                        <th>Meeting Link</th>
                        <th>Reschedule</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="slot in slots" :key="slot.id">
                        <td>
                            <input
                                v-if="!slot.evaluated"
                                type="date"
                                v-model="slot.date"
                                :min="examStart"
                                :max="examEnd"
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
                        <td>{{ slot.maximum_capacity }}</td>
                        <td>{{ slot.available_seats }}</td>
                        <td>{{ slot.booked_seats }}</td>
                        <td>{{ slot.status }}</td>
                        <td>
                            <a v-if="slot.meeting_link"
                               :href="slot.meeting_link"
                               target="_blank">
                                Open Link
                            </a>
                            <span v-else>Not Available</span>
                        </td>
                        <td>
                            <button
                                v-if="!slot.evaluated"
                                class="save-btn"
                                @click="rescheduleSlot(slot)"
                            >
                                Save
                            </button>
                            <span v-else>Marks given</span>
                        </td>
                    </tr>

                    <tr v-if="slots.length === 0">
                        <td colspan="10">No slots available</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const slots = ref([])
const examinationName = ref('')
const examStart = ref('')
const examEnd = ref('')
const message = ref('')
const messageOk = ref(false)

const authHeaders = () => ({
    Authorization: 'Bearer ' + localStorage.getItem('access_token')
})

const fetchSlots = async () => {
    try {
        const response = await axios.get(
            `http://127.0.0.1:5000/view_slot/${route.params.id}`,
            { headers: authHeaders() }
        )

        examinationName.value = response.data.examination_name
        examStart.value = String(response.data.exam_start_time || '').slice(0, 10)
        examEnd.value = String(response.data.exam_end_time || '').slice(0, 10)
        slots.value = response.data.data

    } catch (error) {
        messageOk.value = false
        message.value = error.response?.data?.message || 'Unable to load slots'
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
        await fetchSlots()
    } catch (error) {
        messageOk.value = false
        message.value = error.response?.data?.message || 'Unable to reschedule slot'
    }
}

const goBack = () => {
    router.push('/admin/examinations')
}

onMounted(() => {
    fetchSlots()
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

.table-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1000px;
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
