import type { Article } from '../types/article'

export const articles: Article[] = [
  {
    id: '1',
    title: 'Serhii Plokhy: History of Ukraine, Russia, Soviet Union, KGB, Nazis & War',
    content: `# Ukraine and Russia: A Complex History

This podcast episode explores the deep historical ties and current conflicts between Ukraine and Russia, examining the complex geopolitical dynamics that have shaped their relationship over centuries...`,
    summary: 'This podcast episode takes a deep dive into the historical and political dynamics of the conflict in Ukraine...',
    author: {
      name: 'Wade Warren',
      avatar: '/avatars/wade.jpg'
    },
    tags: ['24小时', '播客', '论文'],
    publishDate: '2024-10-08',
    coverImage: '/images/article-1.jpg'
  },
  {
    id: '2',
    title: '人工智能发展现状与未来趋势分析',
    content: `# AI发展现状分析

近年来，人工智能技术发展迅速，从机器学习到深度学习，从计算机视觉到自然语言处理，各个领域都取得了突破性进展...`,
    summary: '本文深入分析了人工智能领域的最新发展动态，探讨了未来可能的发展方向...',
    author: {
      name: 'Arlene McCoy',
      avatar: '/avatars/arlene.jpg'
    },
    tags: ['微信', '论文', '视频'],
    publishDate: '2024-10-08',
    coverImage: '/images/article-2.jpg'
  },
  {
    id: '3',
    title: '全球气候变化与可持续发展',
    content: `# 气候变化的挑战与对策

全球气候变化已成为人类面临的最大挑战之一。本文将从科学、政策和社会角度探讨这一问题...`,
    summary: '探讨全球气候变化带来的挑战，以及可能的解决方案...',
    author: {
      name: 'Esther Howard',
      avatar: '/avatars/esther.jpg'
    },
    tags: ['24小时', '播客'],
    publishDate: '2024-10-08',
    coverImage: '/images/article-3.jpg'
  },
  {
    id: '4',
    title: '数字经济时代的创新与创业',
    content: `# 数字经济新机遇

数字技术的快速发展正在重塑全球经济格局，为创新创业带来新的机遇与挑战...`,
    summary: '分析数字经济时代的创新趋势和创业机会...',
    author: {
      name: 'Brooklyn Simmons',
      avatar: '/avatars/brooklyn.jpg'
    },
    tags: ['微信', '视频'],
    publishDate: '2024-10-08',
    coverImage: '/images/article-4.jpg'
  },
  {
    id: '5',
    title: '后疫情时代的全球化新趋势',
    content: `# 全球化的新变局

新冠疫情深刻改变了全球化进程，本文将探讨后疫情时代全球化的新特征和发展趋势...`,
    summary: '探讨疫情后全球化的新特征和未来发展趋势...',
    author: {
      name: 'Robert Fox',
      avatar: '/avatars/robert.jpg'
    },
    tags: ['论文', '24小时'],
    publishDate: '2024-10-08',
    coverImage: '/images/article-5.jpg'
  }
]
