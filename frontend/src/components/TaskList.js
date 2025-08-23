import React, { useState } from 'react';
import { Card, Table, Tag, Progress, Button, Space, Popconfirm, message, Tooltip, Modal, Typography, Divider } from 'antd';
import { 
  DownloadOutlined, 
  DeleteOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  FileTextOutlined,
  EyeOutlined,
  SettingOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Text } = Typography;

const TaskList = ({ tasks, onDeleteTask, onDownloadResult }) => {
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [currentLogs, setCurrentLogs] = useState([]);
  const [currentTask, setCurrentTask] = useState(null);
  
  // 获取状态标签
  const getStatusTag = (status) => {
    const statusConfig = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: '等待中' },
      running: { color: 'processing', icon: <LoadingOutlined />, text: '运行中' },
      completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
      failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 获取模式标签
  const getModeTag = (mode) => {
    return mode === '2' ? 
      <Tag color="orange">热门模式</Tag> : 
      <Tag color="blue">普通模式</Tag>;
  };

  // 格式化时间
  const formatTime = (timeStr) => {
    if (!timeStr) return '-';
    return dayjs(timeStr).format('YYYY-MM-DD HH:mm:ss');
  };

  // 计算运行时间
  const getDuration = (startTime, endTime) => {
    if (!startTime) return '-';
    const start = dayjs(startTime);
    const end = endTime ? dayjs(endTime) : dayjs();
    const duration = end.diff(start, 'second');
    
    if (duration < 60) return `${duration}秒`;
    if (duration < 3600) return `${Math.floor(duration / 60)}分钟`;
    return `${Math.floor(duration / 3600)}小时${Math.floor((duration % 3600) / 60)}分钟`;
  };

  // 处理删除任务
  const handleDelete = async (taskId) => {
    try {
      const result = await onDeleteTask(taskId);
      if (result.success) {
        message.success('任务已删除');
      } else {
        message.error(result.error || '删除失败');
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 处理下载结果
  const handleDownload = (taskId) => {
    onDownloadResult(taskId);
  };

  // 查看日志
  const handleViewLogs = (record) => {
    setCurrentTask(record);
    setCurrentLogs(record.logs || []);
    setLogModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 120,
      render: (text) => (
        <Tooltip title={text}>
          <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
            {text.slice(-8)}
          </span>
        </Tooltip>
      )
    },
    {
      title: '主题',
      dataIndex: 'theme_id',
      key: 'theme_id',
      width: 100,
      render: (themeId) => {
        const themeNames = {
          '36': '亚洲无码',
          '37': '亚洲有码',
          '2': '国产原创',
          '103': '高清中文字幕',
          '104': '素人原创',
          '39': '动漫原创',
          '152': '韩国主播'
        };
        return themeNames[themeId] || themeId;
      }
    },
    {
      title: '模式',
      dataIndex: 'mode',
      key: 'mode',
      width: 100,
      render: (mode) => getModeTag(mode)
    },
    {
      title: '页面范围',
      key: 'page_range',
      width: 120,
      render: (_, record) => {
        if (record.mode === '2') return '热门';
        if (record.start_page === record.end_page) {
          return `第${record.start_page}页`;
        }
        return `第${record.start_page}-${record.end_page}页`;
      }
    },
    {
      title: '代理',
      dataIndex: 'proxy',
      key: 'proxy',
      width: 100,
      render: (proxy) => {
        if (!proxy) return <Tag color="default">无代理</Tag>;
        return (
          <Tooltip title={proxy}>
            <Tag color="green" icon={<SettingOutlined />}>
              已启用
            </Tag>
          </Tooltip>
        );
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress, record) => {
        if (record.status === 'pending') return '-';
        if (record.status === 'completed') return '100%';
        if (record.status === 'failed') return '-';
        return (
          <Progress 
            percent={progress} 
            size="small" 
            status={record.status === 'running' ? 'active' : 'normal'}
          />
        );
      }
    },
    {
      title: '磁力链接数',
      dataIndex: 'found_links',
      key: 'found_links',
      width: 100,
      render: (found, record) => {
        if (record.status === 'completed') {
          return (
            <Tag color="green" icon={<FileTextOutlined />}>
              {found} 个
            </Tag>
          );
        }
        return '-';
      }
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 150,
      render: (time) => formatTime(time)
    },
    {
      title: '运行时间',
      key: 'duration',
      width: 120,
      render: (_, record) => getDuration(record.start_time, record.end_time)
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看日志">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewLogs(record)}
            />
          </Tooltip>
          {record.status === 'completed' && (
            <Tooltip title="下载结果">
              <Button
                type="primary"
                size="small"
                icon={<DownloadOutlined />}
                onClick={() => handleDownload(record.task_id)}
              >
                下载
              </Button>
            </Tooltip>
          )}
          <Popconfirm
            title="确定要删除这个任务吗？"
            onConfirm={() => handleDelete(record.task_id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除任务">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <>
      <Card 
        title={
          <Space>
            <FileTextOutlined />
            任务列表
            <Tag color="blue">{tasks.length}</Tag>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="task_id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
          scroll={{ x: 1400 }}
          size="small"
          locale={{
            emptyText: (
              <div style={{ padding: '40px 0' }}>
                <FileTextOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                <p style={{ marginTop: 16, color: '#999' }}>暂无任务</p>
              </div>
            )
          }}
        />
      </Card>

      {/* 日志查看模态框 */}
      <Modal
        title={
          <Space>
            <EyeOutlined />
            任务日志
            {currentTask && (
              <Tag color="blue">
                {currentTask.theme_id} - {currentTask.mode === '2' ? '热门模式' : `第${currentTask.start_page}-${currentTask.end_page}页`}
              </Tag>
            )}
          </Space>
        }
        open={logModalVisible}
        onCancel={() => setLogModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setLogModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
        bodyStyle={{ maxHeight: '60vh', overflow: 'auto' }}
      >
        {currentLogs.length > 0 ? (
          <div>
            {currentLogs.map((log, index) => (
              <div key={index} style={{ 
                padding: '4px 0', 
                borderBottom: index < currentLogs.length - 1 ? '1px solid #f0f0f0' : 'none',
                fontFamily: 'monospace',
                fontSize: '12px'
              }}>
                <Text code>{log}</Text>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            <FileTextOutlined style={{ fontSize: '48px', marginBottom: 16 }} />
            <p>暂无日志记录</p>
          </div>
        )}
      </Modal>
    </>
  );
};

export default TaskList;

