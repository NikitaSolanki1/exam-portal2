
<template>
    <Navbar />

    <div class="content">

        <div class="page-heading">
            <div>
                <h2>Create Examination</h2>
                <p>Add a new examination to the portal</p>
            </div>

            <button class="back-btn" @click="router.push('/admin/examinations')">
                Back to Examinations
            </button>
        </div>

        <div class="form-box">

            <h3>Create Examination</h3>

            <form @submit.prevent="createExamination">

                <div class="form-grid">

                    <div class="form-group full-width">
                        <label>Select Course</label>
                        <select v-model="form.course_id" required>
                            <option value="">Select Course</option>
                            <option
                                v-for="course in courses"
                                :key="course.id"
                                :value="course.id"
                            >
                                {{ course.course_code }} - {{ course.course_name }}
                            </option>
                        </select>
                    </div>

                    <div class="form-group full-width">
                        <label>Exam Name</label>
                        <input
                            v-model="form.exam_name"
                            type="text"
                            placeholder="Enter exam name"
                            required
                        >
                    </div>

                    <div class="form-group full-width">
                        <label>Select Examiner</label>
                        <select v-model="form.examinor_id" required>
                            <option value="">Choose Examiner</option>
                            <option
                                v-for="examiner in examiners"
                                :key="examiner.id"
                                :value="examiner.id"
                            >
                                {{ examiner.name }} ({{ examiner.email }})
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Slot Start Date</label>
                        <input
                            v-model="form.slot_start_date"
                            type="date"
                            :min="today"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Slot End Date</label>
                        <input
                            v-model="form.slot_end_date"
                            type="date"
                            :min="form.slot_start_date || today"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Booking Start Date & Time</label>
                        <input
                            v-model="form.booking_start_time"
                            type="datetime-local"
                            :min="minBookingDate"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Booking End Date & Time</label>
                        <input
                            v-model="form.booking_end_time"
                            type="datetime-local"
                            :min="form.booking_start_time || minBookingDate"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Exam Start Date</label>
                        <input
                            v-model="form.exam_start_date"
                            type="date"
                            :min="minExamDate"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>Exam End Date</label>
                        <input
                            v-model="form.exam_end_date"
                            type="date"
                            :min="form.exam_start_date || minExamDate"
                            required
                        >
                    </div>

                </div>

                <p class="message">{{ message }}</p>

                <div class="form-actions">
                    <button type="submit" class="save-btn">
                        Create Examination
                    </button>

                    <button
                        type="button"
                        class="cancel-btn"
                        @click="router.push('/admin/examinations')"
                    >
                        Cancel
                    </button>
                </div>

            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Navbar from './components/Navbar.vue'

const router = useRouter()

const message = ref('')
const examiners = ref([])
const courses = ref([])

const form = ref({
    course_id: '',
    exam_name: '',
    examinor_id: '',
    slot_start_date: '',
    slot_end_date: '',
    booking_start_time: '',
    booking_end_time: '',
    exam_start_date: '',
    exam_end_date: ''
})

const token = localStorage.getItem('access_token')

const today = new Date().getFullYear() + '-' +
    String(new Date().getMonth() + 1).padStart(2, '0') + '-' +
    String(new Date().getDate()).padStart(2, '0')

const addDays = (date, days) => {
    if (!date) return ''

    const newDate = new Date(date + 'T00:00:00')
    newDate.setDate(newDate.getDate() + days)

    return newDate.getFullYear() + '-' +
        String(newDate.getMonth() + 1).padStart(2, '0') + '-' +
        String(newDate.getDate()).padStart(2, '0')
}

const minBookingDate = computed(() => {
    return form.value.slot_end_date
        ? addDays(form.value.slot_end_date, 1) + 'T00:00'
        : ''
})

const minExamDate = computed(() => {
    return form.value.booking_end_time
        ? addDays(form.value.booking_end_time.slice(0, 10), 1)
        : ''
})

const getCourses = async () => {
    try {
        const response = await axios.get(
            'http://127.0.0.1:5000/courses',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        courses.value = response.data.filter(course =>
            course.status === 'Active'
        )

    } catch (error) {
        message.value = 'Unable to load courses'
    }
}

const getExaminers = async () => {
    try {
        const response = await axios.get(
            'http://127.0.0.1:5000/provide_examinor_details',
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        examiners.value = response.data.data

    } catch (error) {
        message.value = 'Unable to load examiners'
    }
}

const createExamination = async () => {
    try {
        const response = await axios.post(
            'http://127.0.0.1:5000/createexamination',
            {
                course_id: form.value.course_id,
                examinor_id: form.value.examinor_id,
                exam_name: form.value.exam_name,
                slot_start_date: form.value.slot_start_date,
                slot_end_date: form.value.slot_end_date,
                booking_start_time: form.value.booking_start_time,
                booking_end_time: form.value.booking_end_time,
                exam_start_time: form.value.exam_start_date,
                exam_end_time: form.value.exam_end_date
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === 'Examination created successfully') {
            router.push('/admin/examinations')
        }

    } catch (error) {
        message.value = error.response?.data?.message ||
            'Unable to create examination'
    }
}

onMounted(() => {
    getCourses()
    getExaminers()
})
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.content {
    min-height: 100vh;
    padding: 30px 35px;
    background: #f5f7f5;
    font-family: Arial, sans-serif;
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

.back-btn {
    background: white;
    color: #2f5d50;
    border: 1px solid #2f5d50;
    padding: 10px 18px;
    border-radius: 4px;
    cursor: pointer;
}

.form-box {
    background: white;
    padding: 28px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    max-width: 950px;
    margin: auto;
}

.form-box h3 {
    text-align: center;
    color: #2f5d50;
    margin: 0 0 25px;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.full-width {
    grid-column: 1 / -1;
}

.form-group label {
    color: #344b40;
    font-weight: 600;
    font-size: 14px;
}

.form-group input,
.form-group select {
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
    background: white;
}

.form-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 25px;
}

.save-btn {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 11px 22px;
    border-radius: 4px;
    cursor: pointer;
}

.cancel-btn {
    background: #eee;
    color: #444;
    border: none;
    padding: 11px 22px;
    border-radius: 4px;
    cursor: pointer;
}

.message {
    text-align: center;
    color: #b33;
}

</style>
