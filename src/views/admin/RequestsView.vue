<template>
  <div class="p-6">
    <div class="bg-white rounded-lg shadow">
      <div class="p-4 border-b">
        <h2 class="text-lg font-medium">文章请求列表</h2>
      </div>
      
      <!-- 表格 -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                URL
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                原文
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                解析内容
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                提交时间
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in requests" :key="request.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ request.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <a :href="request.url" target="_blank" class="text-blue-600 hover:underline">
                  {{ request.url }}
                </a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ truncateText(request.content) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ truncateText(request.parsed_content) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(request.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': request.status === 'processed',
                    'bg-yellow-100 text-yellow-800': request.status === 'pending',
                    'bg-red-100 text-red-800': request.status === 'rejected'
                  }">
                  {{ getStatusText(request.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex gap-2">
                  <button 
                    @click="handleEdit(request)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    编辑
                  </button>
                  <button 
                    @click="handleFetchContent(request)"
                    class="text-green-600 hover:text-green-900"
                  >
                    获取原文
                  </button>
                  <button 
                    @click="handleParse(request)"
                    class="text-purple-600 hover:text-purple-900"
                  >
                    解析
                  </button>
                  <button 
                    @click="handleProcess(request)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    处理
                  </button>
                  <button 
                    @click="handleReject(request)"
                    class="text-red-600 hover:text-red-900"
                  >
                    拒绝
                  </button>
                  <button 
                    @click="handleDelete(request)"
                    class="text-gray-600 hover:text-gray-900"
                  >
                    删除
                  </button>
                  <button 
                    @click="handleFullProcess(request)"
                    class="text-purple-600 hover:text-purple-900"
                  >
                    一键处理
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑请求"
      width="600px"
      :modal="true"
      :close-on-click-modal="false"
      destroy-on-close
      center
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">URL</label>
          <input 
            v-model="editForm.url"
            type="text"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">原文内容</label>
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入原文内容"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">解析内容</label>
          <el-input
            v-model="editForm.parsed_content"
            type="textarea"
            :rows="10"
            placeholder="请输入解析内容"
            class="w-full"
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { format } from 'date-fns'
import { ElMessage, ElMessageBox, ElDialog, ElButton, ElInput } from 'element-plus'
import { supabase } from '../../supabaseClient'

interface Request {
  id: number
  url: string
  content?: string
  parsed_content?: string
  created_at: string
  status: 'pending' | 'processed' | 'rejected'
}

const requests = ref<Request[]>([])

const fetchRequests = async () => {
  try {
    const { data, error } = await supabase
      .from('keep_article_requests')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    requests.value = data
  } catch (error) {
    console.error('获取请求列表失败:', error)
    ElMessage.error('获取请求列表失败')
  }
}

const formatDate = (date: string) => {
  return format(new Date(date), 'yyyy-MM-dd HH:mm:ss')
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processed: '已处理',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

const handleProcess = async (request: Request) => {
  try {
    const { error } = await supabase
      .from('keep_article_requests')
      .update({ status: 'processed' })
      .eq('id', request.id)

    if (error) throw error
    ElMessage.success('已标记为处理完成')
    await fetchRequests()
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error('处理失败')
  }
}

const handleReject = async (request: Request) => {
  try {
    const { error } = await supabase
      .from('keep_article_requests')
      .update({ status: 'rejected' })
      .eq('id', request.id)

    if (error) throw error
    ElMessage.success('已标记为已拒绝')
    await fetchRequests()
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error('拒绝失败')
  }
}

const handleDelete = async (request: Request) => {
  try {
    await ElMessageBox.confirm('确定要删除这条请求吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const { error } = await supabase
      .from('keep_article_requests')
      .delete()
      .eq('id', request.id)

    if (error) throw error
    ElMessage.success('删除成功')
    await fetchRequests()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 添加编辑相关的状态
const showEditDialog = ref(false)
const editForm = ref<Partial<Request>>({})

// 编辑处理函数
const handleEdit = (request: Request) => {
  editForm.value = {
    id: request.id,
    url: request.url,
    content: request.content,
    parsed_content: request.parsed_content
  }
  showEditDialog.value = true
}

// 提交编辑
const submitEdit = async () => {
  try {
    const { error } = await supabase
      .from('keep_article_requests')
      .update({
        url: editForm.value.url,
        content: editForm.value.content,
        parsed_content: editForm.value.parsed_content
      })
      .eq('id', editForm.value.id)

    if (error) throw error

    ElMessage.success('更新成功')
    showEditDialog.value = false
    await fetchRequests() // 刷新列表
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败，请重试')
  }
}

// 添加文本截断函数
const truncateText = (text?: string) => {
  if (!text) return '-'
  return text.length > 10 ? text.slice(0, 10) + '...' : text
}

// 添加获取原文处理函数
const handleFetchContent = async (request: Request) => {
  try {
    ElMessage.info('正在获取原文...')
    const response = await fetch('/api/fetch-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        id: request.id,
        url: request.url 
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '获取原文失败')
    }

    const { message } = await response.json()
    ElMessage.success(message)
    
    // 开始轮询状态
    const checkStatus = setInterval(async () => {
      const { data, error } = await supabase
        .from('keep_article_requests')
        .select('status, content, error_message')
        .eq('id', request.id)
        .single()

      if (error) {
        clearInterval(checkStatus)
        ElMessage.error('检查状态失败')
        return
      }

      if (data.status === 'processed') {
        clearInterval(checkStatus)
        ElMessage.success('原文获取成功')
        await fetchRequests() // 刷新列表
      } else if (data.status === 'failed') {
        clearInterval(checkStatus)
        ElMessage.error(`获取失败: ${data.error_message}`)
        await fetchRequests()
      }
    }, 2000) // 每2秒检查一次状态

    // 60秒后停止轮询
    setTimeout(() => {
      clearInterval(checkStatus)
    }, 60000)

  } catch (error) {
    console.error('获取原文失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '获取原文失败，请重试')
  }
}

// 添加解析处理函数
const handleParse = async (request: Request) => {
  try {
    if (!request.content) {
      ElMessage.warning('请先获取原文')
      return
    }

    ElMessage.info('开始解析...')
    const response = await fetch('/api/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        url: request.url,
        content: request.content,
        id: request.id
      })
    })

    if (!response.ok) throw new Error('解析失败')

    const { message } = await response.json()
    ElMessage.success(message)
    
    // 开始轮询状态
    const checkStatus = setInterval(async () => {
      const { data, error } = await supabase
        .from('keep_article_requests')
        .select('status, error_message')
        .eq('id', request.id)
        .single()

      if (error) {
        clearInterval(checkStatus)
        ElMessage.error('检查状态失败')
        return
      }

      if (data.status === 'processed') {
        clearInterval(checkStatus)
        ElMessage.success('解析完成')
        await fetchRequests()
      } else if (data.status === 'failed') {
        clearInterval(checkStatus)
        ElMessage.error(`解析失败: ${data.error_message}`)
        await fetchRequests()
      }
    }, 2000) // 每2秒检查一次状态

    // 60秒后停止轮询
    setTimeout(() => {
      clearInterval(checkStatus)
    }, 60000)

  } catch (error) {
    console.error('解析失败:', error)
    ElMessage.error('解析失败，请重试')
  }
}

// 添加一键处理函数
const handleFullProcess = async (request: Request) => {
  try {
    ElMessage.info('开始处理...')
    const response = await fetch('/api/workflow/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        id: request.id,
        url: request.url 
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '处理失败')
    }

    const { message, steps } = await response.json()
    
    // 显示处理步骤
    steps.forEach((step: string) => {
      ElMessage.success(step)
    })
    
    await fetchRequests() // 刷新列表
    
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '处理失败，请重试')
  }
}

onMounted(fetchRequests)
</script>

<style>
.el-dialog {
  margin-top: 8vh !important;
}
</style> 