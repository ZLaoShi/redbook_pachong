import request from './request'

/**
 * 获取当前用户的任务列表
 * @param {Object} params 查询参数
 * @param {number} params.skip 跳过的数量
 * @param {number} params.limit 返回的数量
 * @returns {Promise<Array>} 返回任务列表
 */
export function getTasks(params = {}) {
  return request({
    url: '/tasks/',
    method: 'get',
    params
  })
}

/**
 * 获取任务详情
 * @param {number} taskId 任务ID
 * @returns {Promise<Object>} 返回任务详情
 */
export function getTaskDetail(taskId) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 创建新任务
 * @param {Object} data 任务数据
 * @param {string} data.blogger_profile_url 博主主页URL
 * @param {string} data.user_cookie 用户Cookie
 * @param {Object} data.scraping_rules 抓取规则
 * @returns {Promise<Object>} 返回创建结果
 */
export function createTask(data) {
  return request({
    url: '/tasks/',
    method: 'post',
    data
  })
}

/**
 * 更新任务
 * @param {number} taskId 任务ID
 * @param {Object} data 更新数据
 * @returns {Promise<Object>} 返回更新结果
 */
export function updateTask(taskId, data) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'put',
    data
  })
}

/**
 * 删除任务
 * @param {number} taskId 任务ID
 * @returns {Promise<Object>} 返回删除结果
 */
export function deleteTask(taskId) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'delete'
  })
}

/**
 * 获取笔记详情
 * @param {number} noteId 笔记ID
 * @returns {Promise<Object>} 返回笔记详情
 */
export function getNoteDetail(noteId) {
  return request({
    url: `/tasks/notes/${noteId}`,
    method: 'get'
  })
}