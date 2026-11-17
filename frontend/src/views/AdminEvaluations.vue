
<template>
  <Navbar />

  <div class="page">
    <div class="container">
      <h2>Submitted Evaluations</h2>
      <p>Review student evaluations and publish examination results.</p>

      <div class="table-box">
        <table>
          <thead>
            <tr>
              <th>Student Name</th>
              <th>Email</th>
              <th>Examination</th>
              <th>Total Marks</th>
              <th>Date</th>
              <th>Exam Status</th>
              <th>Result</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="item in evaluations" :key="item.id">
              <td>{{ item.student_name }}</td>
              <td>{{ item.student_email }}</td>
              <td>{{ item.exam_name }}</td>
              <td>{{ item.total_marks }}</td>
              <td>{{ item.evaluation_date }}</td>

              <td>
                <span v-if="item.results_published" class="published">
                  Finished
                </span>
                <span v-else class="pending">
                  Ongoing
                </span>
              </td>

              <td>
                <span v-if="item.results_published" class="published">
                  Published
                </span>
                <span v-else class="pending">
                  Pending
                </span>
              </td>

              <td>
                <button class="view-btn" @click="viewDetails(item.id)">
                  View
                </button>

                <button
                  v-if="!item.results_published"
                  class="publish-btn"
                  @click="publishResult(item)"
                >
                  Publish Result
                </button>
              </td>
            </tr>

            <tr v-if="evaluations.length === 0">
              <td colspan="8">No evaluations submitted yet.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="selectedEvaluation" class="details-box">
        <div class="details-heading">
          <h3>Evaluation Details</h3>
          <button class="close-btn" @click="selectedEvaluation = null">
            Close
          </button>
        </div>

        <p><b>Student Name:</b> {{ selectedEvaluation.student_name }}</p>
        <p><b>Email:</b> {{ selectedEvaluation.student_email }}</p>
        <p><b>Examination:</b> {{ selectedEvaluation.exam_name }}</p>
        <p><b>Total Marks:</b> {{ selectedEvaluation.total_marks }}</p>
        <p><b>Remarks:</b> {{ selectedEvaluation.remarks }}</p>

        <h3>Rubric Marks</h3>

        <table>
          <thead>
            <tr>
              <th>Criterion</th>
              <th>Maximum Marks</th>
              <th>Marks Obtained</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(rubric, index) in selectedEvaluation.rubrics" :key="index">
              <td>{{ rubric.criterion_name }}</td>
              <td>{{ rubric.maximum_marks }}</td>
              <td>{{ rubric.marks_obtained }}</td>
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
import { ref, onMounted } from 'vue'

const evaluations = ref([])
const selectedEvaluation = ref(null)

const getEvaluations = async () => {
  try {
    const token = localStorage.getItem("access_token")

    const response = await axios.get(
      'http://127.0.0.1:5000/admin/evaluations',
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    evaluations.value = response.data.data

  } catch (error) {
    console.log(error.response?.data || error.message)
  }
}

const viewDetails = async (evaluation_id) => {
  try {
    const token = localStorage.getItem("access_token")

    const response = await axios.get(
      'http://127.0.0.1:5000/admin/evaluation-details/' + evaluation_id,
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    selectedEvaluation.value = response.data

  } catch (error) {
    console.log(error.response?.data || error.message)
  }
}

const publishResult = async (item) => {
  try {
    const token = localStorage.getItem("access_token")

    await axios.post(
      'http://127.0.0.1:5000/admin/publish-result/' + item.exam_id,
      {},
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    await getEvaluations()

  } catch (error) {
    console.log(error.response?.data || error.message)
  }
}

onMounted(() => {
  getEvaluations()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 30px 20px;
}

.container {
  max-width: 1100px;
  margin: auto;
}

h2 {
  color: #333;
}

.container p {
  color: #666;
}

.table-box,
.details-box {
  background: white;
  border: 1px solid #ddd;
  padding: 20px;
  margin-top: 25px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 13px;
  border-bottom: 1px solid #ddd;
  text-align: left;
  white-space: nowrap;
}

th {
  background: #2f5d50;
  color: white;
}

.view-btn,
.publish-btn,
.close-btn {
  border: none;
  padding: 8px 12px;
  color: white;
  cursor: pointer;
  margin-right: 5px;
}

.view-btn {
  background: #555;
}

.publish-btn {
  background: #2f5d50;
}

.close-btn {
  background: #555;
}

.published {
  color: green;
  font-weight: bold;
}

.pending {
  color: #b7791f;
  font-weight: bold;
}

.details-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.details-box p {
  color: #333;
}
</style>

