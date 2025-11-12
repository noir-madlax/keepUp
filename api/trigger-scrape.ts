import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(
  request: VercelRequest,
  response: VercelResponse
) {
  // 只允许 POST 请求
  if (request.method !== 'POST') {
    return response.status(405).json({ error: 'Method not allowed' })
  }

  const { site } = request.query
  const githubToken = process.env.GITHUB_TOKEN
  const githubRepo = process.env.GITHUB_REPO || 'keepUp'
  const githubOwner = process.env.GITHUB_OWNER
  const githubBranch = process.env.GITHUB_BRANCH || 'main'

  if (!githubToken) {
    return response.status(500).json({ error: 'GitHub Token未配置' })
  }

  if (!githubOwner) {
    return response.status(500).json({ error: 'GitHub Owner未配置' })
  }

  // 确定要触发的workflow
  let workflowFile: string
  if (site === 'openrouter') {
    workflowFile = 'monitor-openrouter.yml'
  } else if (site === 'cursor') {
    workflowFile = 'monitor-cursor.yml'
  } else if (site === 'tikhub') {
    workflowFile = 'monitor-tikhub.yml'
  } else if (site === 'google') {
    workflowFile = 'monitor-google.yml'
  } else if (site === 'dajiala') {
    workflowFile = 'monitor-dajiala.yml'
  } else if (site === 'supadata') {
    workflowFile = 'monitor-supadata.yml'
  } else if (site === 'tencent') {
    workflowFile = 'monitor-tencent.yml'
  } else if (!site) {
    workflowFile = 'monitor-all.yml'
  } else {
    return response.status(400).json({ error: '无效的site参数' })
  }

  try {
    // 触发 GitHub Actions workflow
    const githubResponse = await fetch(
      `https://api.github.com/repos/${githubOwner}/${githubRepo}/actions/workflows/${workflowFile}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ref: githubBranch,
        }),
      }
    )

    if (!githubResponse.ok) {
      const errorText = await githubResponse.text()
      console.error('GitHub API Error:', errorText)
      return response.status(githubResponse.status).json({ 
        error: `触发GitHub Actions失败: ${errorText}` 
      })
    }

    return response.status(200).json({ 
      success: true,
      message: `已触发 ${site || '所有站点'} 的数据抓取`,
      workflow: workflowFile
    })
  } catch (error: any) {
    console.error('Error triggering scrape:', error)
    return response.status(500).json({ 
      error: error.message || '触发失败'
    })
  }
}

