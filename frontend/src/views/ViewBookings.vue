
<template>
    <Navbar />

    <div class="page">
        <div class="heading">
            <h2>All Bookings</h2>
            <p>View and manage student examination bookings</p>
        </div>

        <div class="table-box">
            <div class="top-section">
                <h3>Booking Details</h3>

                <input
                    type="text"
                    v-model="search"
                    placeholder="Search student, exam or examiner..."
                />
            </div>

            <p v-if="message" class="message">{{ message }}</p>

            <table>
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>Student Name</th>
                        <th>Email</th>
                        <th>Examination</th>
                        <th>Examiner</th>
                        <th>Slot Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Booking Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="booking in filteredBookings" :key="booking.id">
                        <td>{{ booking.id }}</td>
                        <td>{{ booking.student_name }}</td>
                        <td>{{ booking.student_email }}</td>
                        <td>{{ booking.examination_name }}</td>
                        <td>{{ booking.examiner_name }}</td>
                        <td>{{ booking.slot_date }}</td>
                        <td>{{ booking.start_time }}</td>
                        <td>{{ booking.end_time }}</td>
                        <td>{{ booking.booking_date }}</td>
                        <td>
                            <span class="status">{{ booking.status }}</span>
                        </td>
                        <td>
                            <button
                                class="action-btn"
                                @click="open_reschedule(booking)"
                            >
                                Reschedule
                            </button>

                            <button
                                class="action-btn reassign-btn"
                                @click="open_reassign(booking)"
                            >
                                Reassign Examiner
                            </button>
                        </td>
                    </tr>

                    <tr v-if="filteredBookings.length === 0">
                        <td colspan="11" class="no-data">
                            No bookings found
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="show_reschedule" class="popup">
            <div class="popup-content">
                <h3>Reschedule Booking</h3>

                <p>
                    <strong>Student:</strong>
                    {{ selected_booking?.student_name }}
                </p>

                <p>
                    <strong>Examination:</strong>
                    {{ selected_booking?.examination_name }}
                </p>

                <label>Select New Slot</label>

                <select v-model="selected_slot">
                    <option value="">Select Slot</option>

                    <option
                        v-for="slot in available_slots"
                        :key="slot.id"
                        :value="slot.id"
                    >
                        {{ slot.date }} |
                        {{ slot.start_time }} - {{ slot.end_time }} |
                        Seats: {{ slot.available_seats }}
                    </option>
                </select>

                <p v-if="reschedule_message" class="message">
                    {{ reschedule_message }}
                </p>

                <div class="popup-buttons">
                    <button
                        class="action-btn"
                        @click="reschedule_booking"
                    >
                        Confirm Reschedule
                    </button>

                    <button
                        class="cancel-btn"
                        @click="show_reschedule = false"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>

        <div v-if="show_reassign" class="popup">
            <div class="popup-content">
                <h3>Reassign Examiner</h3>

                <p>
                    <strong>Student:</strong>
                    {{ selected_booking?.student_name }}
                </p>

                <p>
                    <strong>Examination:</strong>
                    {{ selected_booking?.examination_name }}
                </p>

                <p>
                    <strong>Current Examiner:</strong>
                    {{ selected_booking?.examiner_name }}
                </p>

                <p class="hint-text">
                    Free examiners (including those with no slots) can be assigned.
                </p>

                <label>Select Free Examiner</label>

                <select v-model="selected_reassign_examiner">
                    <option value="">Select Examiner</option>

                    <option
                        v-for="opt in reassign_slots"
                        :key="opt.examiner_id"
                        :value="opt.examiner_id"
                    >
                        {{ opt.examiner_name }}
                        {{ opt.will_create_slot ? '(Free — will create slot)' : '(Free slot available)' }}
                        | {{ opt.date }} {{ opt.start_time }}-{{ opt.end_time }}
                    </option>
                </select>

                <p v-if="reassign_message" class="message">
                    {{ reassign_message }}
                </p>

                <div class="popup-buttons">
                    <button
                        class="action-btn"
                        @click="reassign_booking"
                    >
                        Confirm Reassign
                    </button>

                    <button
                        class="cancel-btn"
                        @click="show_reassign = false"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const bookings = ref([])
const search = ref('')
const message = ref('')

const show_reschedule = ref(false)
const selected_booking = ref(null)
const selected_slot = ref('')
const available_slots = ref([])
const reschedule_message = ref('')

const show_reassign = ref(false)
const selected_reassign_examiner = ref('')
const reassign_slots = ref([])
const reassign_message = ref('')

const fetchBookings = async () => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(
            'http://127.0.0.1:5000/admin/bookings',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        bookings.value = response.data.data

    } catch (error) {
        console.log(error.response?.data || error.message)
        message.value = error.response?.data?.message || 'Unable to load bookings'
    }
}

const filteredBookings = computed(() => {
    return bookings.value.filter(booking => {
        return (
            booking.student_name?.toLowerCase().includes(search.value.toLowerCase()) ||
            booking.student_email?.toLowerCase().includes(search.value.toLowerCase()) ||
            booking.examination_name?.toLowerCase().includes(search.value.toLowerCase()) ||
            booking.examiner_name?.toLowerCase().includes(search.value.toLowerCase()) ||
            booking.status?.toLowerCase().includes(search.value.toLowerCase())
        )
    })
})


const open_reschedule = async (booking) => {
    selected_booking.value = booking
    selected_slot.value = ''
    reschedule_message.value = ''
    available_slots.value = []

    show_reassign.value = false

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(
            `http://127.0.0.1:5000/admin/available-slots/${booking.id}`,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        available_slots.value = response.data.data
        show_reschedule.value = true

        if (available_slots.value.length === 0) {
            reschedule_message.value = 'No other available slots found'
        }

    } catch (error) {
        console.log(error.response?.data || error.message)
        message.value = error.response?.data?.message || 'Unable to load slots'
    }
}

const reschedule_booking = async () => {
    if (!selected_slot.value) {
        reschedule_message.value = 'Please select a slot'
        return
    }

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            `http://127.0.0.1:5000/admin/reschedule-booking/${selected_booking.value.id}`,
            {
                slot_id: selected_slot.value
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message
        show_reschedule.value = false

        await fetchBookings()

    } catch (error) {
        console.log(error.response?.data || error.message)
        reschedule_message.value = error.response?.data?.message || 'Unable to reschedule booking'
    }
}


const open_reassign = async (booking) => {
    selected_booking.value = booking
    selected_reassign_examiner.value = ''
    reassign_message.value = ''
    reassign_slots.value = []

    show_reschedule.value = false

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(
            `http://127.0.0.1:5000/admin/reassign-slots/${booking.id}`,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        reassign_slots.value = response.data.data || []
        show_reassign.value = true

        if (reassign_slots.value.length === 0) {
            reassign_message.value = 'No free examiners available'
        }

    } catch (error) {
        console.log(error.response?.data || error.message)
        message.value = error.response?.data?.message || 'Unable to load free examiners'
    }
}

const reassign_booking = async () => {
    if (!selected_reassign_examiner.value) {
        reassign_message.value = 'Please select an examiner'
        return
    }

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            `http://127.0.0.1:5000/admin/reassign-booking/${selected_booking.value.id}`,
            {
                examiner_id: selected_reassign_examiner.value
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message
        show_reassign.value = false

        await fetchBookings()

    } catch (error) {
        console.log(error.response?.data || error.message)
        reassign_message.value = error.response?.data?.message || 'Unable to reassign examiner'
    }
}

onMounted(() => {
    fetchBookings()
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
    margin-bottom: 8px;
}

.heading p {
    color: #666;
}

.table-box {
    background: white;
    padding: 25px;
    border-radius: 10px;
    overflow-x: auto;
}

.top-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    gap: 15px;
}

.top-section h3 {
    color: #2f5d50;
}

input {
    padding: 10px 14px;
    width: 300px;
    border: 1px solid #ccc;
    border-radius: 6px;
    outline: none;
}

input:focus {
    border-color: #2f5d50;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1200px;
}

th {
    background: #2f5d50;
    color: white;
    padding: 13px;
    text-align: left;
    white-space: nowrap;
}

td {
    padding: 13px;
    border-bottom: 1px solid #eee;
    color: #444;
    white-space: nowrap;
}

tr:hover {
    background: #f5f8f6;
}

.status {
    background: #e3f2e9;
    color: #2f5d50;
    padding: 5px 10px;
    border-radius: 5px;
}

.no-data {
    text-align: center;
    padding: 25px;
    color: #777;
}

.message {
    color: #b33;
    margin-bottom: 15px;
}

.hint-text {
    color: #555;
    font-size: 0.92rem;
    margin: 8px 0 12px;
}

.action-btn {
    display: block;
    background: #2f5d50;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
    white-space: nowrap;
    margin: 5px 0;
}

.reassign-btn {
    background: #527c6c;
}

.cancel-btn {
    background: #ddd;
    color: #333;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
}

.popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.popup-content {
    background: white;
    padding: 25px;
    width: 450px;
    border-radius: 10px;
}

.popup-content h3 {
    color: #2f5d50;
    margin-bottom: 15px;
}

.popup-content p {
    margin-bottom: 12px;
}

.popup-content label {
    display: block;
    margin-top: 15px;
}

.popup-content select {
    width: 100%;
    padding: 10px;
    margin: 10px 0 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

.popup-buttons {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}
</style>
