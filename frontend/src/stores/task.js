import { defineStore } from 'pinia'
import axios from 'axios'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    currentTask: null,
    currentNote: null,
    loading: false,
    error: null
  }),
  
  getters: {
    getTasks: (state) => state.tasks,
    getCurrentTask: (state) => state.currentTask,
    getCurrentNote: (state) => state.currentNote
  },
  
  actions: {
    async fetchTasks() {
      this.loading = true
      try {
        const response = await axios.get('/api/v1/tasks/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        this.tasks = response.data
        this.error = null
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
        this.error = error.response?.data?.detail || '获取任务列表失败'
      } finally {
        this.loading = false
      }
    },
    
    async fetchTaskDetail(taskId) {
      this.loading = true
      try {
        const response = await axios.get(`/api/v1/tasks/${taskId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        this.currentTask = response.data
        this.error = null
      } catch (error) {
        console.error(`Failed to fetch task ${taskId}:`, error)
        this.error = error.response?.data?.detail || '获取任务详情失败'
      } finally {
        this.loading = false
      }
    },
    
    async fetchNoteDetail(noteId) {
      this.loading = true
      try {
        const response = await axios.get(`/api/v1/tasks/notes/${noteId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        this.currentNote = response.data
        this.error = null
      } catch (error) {
        console.error(`Failed to fetch note ${noteId}:`, error)
        this.error = error.response?.data?.detail || '获取笔记详情失败'
      } finally {
        this.loading = false
      }
    },
    
    async createTask(taskData) {
      this.loading = true
      try {
        const response = await axios.post('/api/v1/tasks/', taskData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        // 更新任务列表
        await this.fetchTasks()
        
        return { success: true, task: response.data }
      } catch (error) {
        console.error('Failed to create task:', error)
        this.error = error.response?.data?.detail || '创建任务失败'
        return { success: false, message: this.error }
      } finally {
        this.loading = false
      }
    }
  }
})