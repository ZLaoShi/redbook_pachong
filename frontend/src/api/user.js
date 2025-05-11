import request from './request'
import qs from 'qs'

/**
 * 用户登录
 * @param {Object} data 登录信息
 * @param {string} data.username 用户名
 * @param {string} data.password 密码
 * @returns {Promise<Object>} 返回登录结果，包含token
 */
export function login(data) {
  return request({
    url: '/login/access-token',
    method: 'post',
    data: qs.stringify(data),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise<Object>} 返回用户信息
 */
export function getUserInfo() {
  return request({
    url: '/users/me',
    method: 'get'
  })
}

/**
 * 注册新用户
 * @param {Object} data 用户信息
 * @param {string} data.username 用户名
 * @param {string} data.password 密码
 * @param {string} data.email 邮箱
 * @returns {Promise<Object>} 返回注册结果
 */
export function register(data) {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}