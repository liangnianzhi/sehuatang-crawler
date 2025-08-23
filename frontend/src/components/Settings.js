import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Switch, 
  Button, 
  message, 
  Space, 
  Divider, 
  Table, 
  Tag, 
  Modal, 
  Select, 
  InputNumber, 
  TimePicker,
  Popconfirm,
  Tooltip,
  Typography
} from 'antd';
import { 
  SettingOutlined, 
  ClockCircleOutlined, 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SaveOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Option } = Select;
const { Text } = Typography;

const Settings = () => {
  const [proxyForm] = Form.useForm();
  const [taskForm] = Form.useForm();
  const [proxyConfig, setProxyConfig] = useState({ proxy_enabled: false, proxy_url: '' });
  const [scheduledTasks, setScheduledTasks] = useState([]);
  const [themes, setThemes] = useState([]);
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [loading, setLoading] = useState(false);

  // 获取代理配置
  const fetchProxyConfig = async () => {
    try {
      const response = await fetch('/api/proxy/config');
      const data = await response.json();
      if (data.success) {
        setProxyConfig(data.data);
        proxyForm.setFieldsValue({
          enabled: data.data.proxy_enabled,
          proxy_url: data.data.proxy_url
        });
      }
    } catch (error) {
      console.error('获取代理配置失败:', error);
    }
  };

  // 获取主题列表
  const fetchThemes = async () => {
    try {
      const response = await fetch('/api/themes');
      const data = await response.json();
      if (data.success) {
        setThemes(data.data);
      }
    } catch (error) {
      console.error('获取主题列表失败:', error);
    }
  };

  // 获取定时任务列表
  const fetchScheduledTasks = async () => {
    try {
      const response = await fetch('/api/scheduled-tasks');
      const data = await response.json();
      if (data.success) {
        setScheduledTasks(data.data);
      }
    } catch (error) {
      console.error('获取定时任务失败:', error);
    }
  };

  useEffect(() => {
    fetchProxyConfig();
    fetchThemes();
    fetchScheduledTasks();
  }, []);

  // 保存代理配置
  const handleSaveProxy = async (values) => {
    try {
      const response = await fetch('/api/proxy/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enabled: values.enabled,
          proxy_url: values.proxy_url
        }),
      });
      const data = await response.json();
      if (data.success) {
        message.success('代理配置已保存');
        fetchProxyConfig();
      } else {
        message.error(data.error || '保存代理配置失败');
      }
    } catch (error) {
      message.error('保存代理配置失败');
    }
  };

  // 创建/编辑定时任务
  const handleSaveTask = async (values) => {
    try {
      setLoading(true);
      
      let scheduleValue = '';
      if (values.schedule_type === 'daily') {
        scheduleValue = values.schedule_time.format('HH:mm');
      } else if (values.schedule_type === 'weekly') {
        scheduleValue = `${values.schedule_day}:${values.schedule_time.format('HH:mm')}`;
      } else if (values.schedule_type === 'interval') {
        scheduleValue = values.interval_minutes.toString();
      }

      const taskData = {
        name: values.name,
        theme_id: values.theme_id,
        mode: values.mode,
        start_page: values.start_page,
        end_page: values.end_page,
        schedule_type: values.schedule_type,
        schedule_value: scheduleValue
      };

      const url = editingTask 
        ? `/api/scheduled-tasks/${editingTask.task_id}`
        : '/api/scheduled-tasks';
      
      const method = editingTask ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });
      
      const data = await response.json();
      if (data.success) {
        message.success(editingTask ? '定时任务更新成功' : '定时任务创建成功');
        setTaskModalVisible(false);
        setEditingTask(null);
        taskForm.resetFields();
        fetchScheduledTasks();
      } else {
        message.error(data.error || '操作失败');
      }
    } catch (error) {
      message.error('操作失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除定时任务
  const handleDeleteTask = async (taskId) => {
    try {
      const response = await fetch(`/api/scheduled-tasks/${taskId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.success) {
        message.success('定时任务删除成功');
        fetchScheduledTasks();
      } else {
        message.error(data.error || '删除失败');
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 启用/禁用定时任务
  const handleToggleTask = async (taskId, enabled) => {
    try {
      const url = `/api/scheduled-tasks/${taskId}/${enabled ? 'enable' : 'disable'}`;
      const response = await fetch(url, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        message.success(enabled ? '定时任务已启用' : '定时任务已禁用');
        fetchScheduledTasks();
      } else {
        message.error(data.error || '操作失败');
      }
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 编辑任务
  const handleEditTask = (record) => {
    setEditingTask(record);
    
    // 解析调度值
    let scheduleTime = dayjs('09:00', 'HH:mm');
    let scheduleDay = 0;
    let intervalMinutes = 60;
    
    if (record.schedule_type === 'daily') {
      scheduleTime = dayjs(record.schedule_value, 'HH:mm');
    } else if (record.schedule_type === 'weekly') {
      const parts = record.schedule_value.split(':');
      scheduleDay = parseInt(parts[0]);
      scheduleTime = dayjs(parts[1], 'HH:mm');
    } else if (record.schedule_type === 'interval') {
      intervalMinutes = parseInt(record.schedule_value);
    }

    taskForm.setFieldsValue({
      name: record.name,
      theme_id: record.theme_id,
      mode: record.mode,
      start_page: record.start_page,
      end_page: record.end_page,
      schedule_type: record.schedule_type,
      schedule_time: scheduleTime,
      schedule_day: scheduleDay,
      interval_minutes: intervalMinutes
    });
    
    setTaskModalVisible(true);
  };

  // 新建任务
  const handleNewTask = () => {
    setEditingTask(null);
    taskForm.resetFields();
    taskForm.setFieldsValue({
      mode: '1',
      start_page: 1,
      end_page: 1,
      schedule_type: 'daily',
      schedule_time: dayjs('09:00', 'HH:mm'),
      schedule_day: 0,
      interval_minutes: 60
    });
    setTaskModalVisible(true);
  };

  // 定时任务表格列定义
  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '主题',
      dataIndex: 'theme_id',
      key: 'theme_id',
      width: 120,
      render: (themeId) => {
        const theme = themes.find(t => t.id === themeId);
        return theme ? theme.name : themeId;
      }
    },
    {
      title: '模式',
      dataIndex: 'mode',
      key: 'mode',
      width: 80,
      render: (mode) => (
        <Tag color={mode === '2' ? 'green' : 'blue'}>
          {mode === '2' ? '热门' : '普通'}
        </Tag>
      )
    },
    {
      title: '页面范围',
      key: 'page_range',
      width: 100,
      render: (_, record) => {
        if (record.mode === '2') return '热门';
        if (record.start_page === record.end_page) {
          return `第${record.start_page}页`;
        }
        return `第${record.start_page}-${record.end_page}页`;
      }
    },
    {
      title: '调度类型',
      dataIndex: 'schedule_type',
      key: 'schedule_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          'daily': '每日',
          'weekly': '每周',
          'interval': '间隔'
        };
        return <Tag color="purple">{typeMap[type] || type}</Tag>;
      }
    },
    {
      title: '调度值',
      dataIndex: 'schedule_value',
      key: 'schedule_value',
      width: 120,
      render: (value, record) => {
        if (record.schedule_type === 'daily') {
          return value;
        } else if (record.schedule_type === 'weekly') {
          const parts = value.split(':');
          const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
          return `${dayNames[parseInt(parts[0])]} ${parts[1]}`;
        } else if (record.schedule_type === 'interval') {
          return `每${value}分钟`;
        }
        return value;
      }
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 80,
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '下次运行',
      dataIndex: 'next_run',
      key: 'next_run',
      width: 150,
      render: (nextRun) => {
        if (!nextRun) return '-';
        return dayjs(nextRun).format('MM-DD HH:mm');
      }
    },
    {
      title: '运行次数',
      dataIndex: 'run_count',
      key: 'run_count',
      width: 80,
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title={record.enabled ? '禁用' : '启用'}>
            <Button
              type="text"
              size="small"
              icon={record.enabled ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={() => handleToggleTask(record.task_id, !record.enabled)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEditTask(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个定时任务吗？"
            onConfirm={() => handleDeleteTask(record.task_id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
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
    <div>
      {/* 代理设置 */}
      <Card 
        title={
          <Space>
            <SettingOutlined />
            代理设置
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Form
          form={proxyForm}
          layout="vertical"
          onFinish={handleSaveProxy}
          initialValues={{
            enabled: false,
            proxy_url: ''
          }}
        >
          <Form.Item
            label="代理设置"
            name="enabled"
            valuePropName="checked"
          >
            <Switch 
              checkedChildren="启用"
              unCheckedChildren="禁用"
            />
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.enabled !== currentValues.enabled}
          >
            {({ getFieldValue }) => {
              const enabled = getFieldValue('enabled');
              if (enabled) {
                return (
                  <Form.Item
                    label="代理地址"
                    name="proxy_url"
                    rules={[
                      { required: true, message: '请输入代理地址' },
                      { 
                        pattern: /^(http|https|socks5):\/\/[\w\-\.]+:\d+$/, 
                        message: '代理格式：http://host:port 或 socks5://host:port' 
                      }
                    ]}
                  >
                    <Input
                      placeholder="代理地址，如：http://127.0.0.1:7890 或 socks5://127.0.0.1:1080"
                      prefix={<SettingOutlined />}
                    />
                  </Form.Item>
                );
              }
              return null;
            }}
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
            >
              保存代理设置
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 定时任务管理 */}
      <Card 
        title={
          <Space>
            <ClockCircleOutlined />
            定时任务管理
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewTask}
          >
            新建定时任务
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={scheduledTasks}
          rowKey="task_id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
          scroll={{ x: 1200 }}
          size="small"
          locale={{
            emptyText: (
              <div style={{ padding: '40px 0', textAlign: 'center' }}>
                <ClockCircleOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                <p style={{ marginTop: 16, color: '#999' }}>暂无定时任务</p>
                <Button type="primary" onClick={handleNewTask}>
                  创建第一个定时任务
                </Button>
              </div>
            )
          }}
        />
      </Card>

      {/* 定时任务编辑模态框 */}
      <Modal
        title={
          <Space>
            <ClockCircleOutlined />
            {editingTask ? '编辑定时任务' : '新建定时任务'}
          </Space>
        }
        open={taskModalVisible}
        onCancel={() => {
          setTaskModalVisible(false);
          setEditingTask(null);
          taskForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={taskForm}
          layout="vertical"
          onFinish={handleSaveTask}
        >
          <Form.Item
            label="任务名称"
            name="name"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="请输入任务名称" />
          </Form.Item>

          <Form.Item
            label="选择主题"
            name="theme_id"
            rules={[{ required: true, message: '请选择主题' }]}
          >
            <Select placeholder="请选择要爬取的主题">
              {themes.map(theme => (
                <Option key={theme.id} value={theme.id}>
                  {theme.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="爬取模式"
            name="mode"
            rules={[{ required: true, message: '请选择爬取模式' }]}
          >
            <Select>
              <Option value="1">普通模式</Option>
              <Option value="2">热门模式</Option>
            </Select>
          </Form.Item>

          <Form.Item label="页面范围">
            <Space>
              <Form.Item
                name="start_page"
                noStyle
                rules={[
                  { required: true, message: '请输入起始页' },
                  { type: 'number', min: 1, message: '起始页必须大于0' }
                ]}
              >
                <InputNumber
                  min={1}
                  max={100}
                  placeholder="起始页"
                  style={{ width: 120 }}
                />
              </Form.Item>
              <span>到</span>
              <Form.Item
                name="end_page"
                noStyle
                rules={[
                  { required: true, message: '请输入结束页' },
                  { type: 'number', min: 1, message: '结束页必须大于0' }
                ]}
              >
                <InputNumber
                  min={1}
                  max={100}
                  placeholder="结束页"
                  style={{ width: 120 }}
                />
              </Form.Item>
            </Space>
          </Form.Item>

          <Divider />

          <Form.Item
            label="调度类型"
            name="schedule_type"
            rules={[{ required: true, message: '请选择调度类型' }]}
          >
            <Select>
              <Option value="daily">每日执行</Option>
              <Option value="weekly">每周执行</Option>
              <Option value="interval">间隔执行</Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.schedule_type !== currentValues.schedule_type}
          >
            {({ getFieldValue }) => {
              const scheduleType = getFieldValue('schedule_type');
              
              if (scheduleType === 'daily') {
                return (
                  <Form.Item
                    label="执行时间"
                    name="schedule_time"
                    rules={[{ required: true, message: '请选择执行时间' }]}
                  >
                    <TimePicker format="HH:mm" placeholder="选择时间" />
                  </Form.Item>
                );
              }
              
              if (scheduleType === 'weekly') {
                return (
                  <>
                    <Form.Item
                      label="星期"
                      name="schedule_day"
                      rules={[{ required: true, message: '请选择星期' }]}
                    >
                      <Select>
                        <Option value={0}>周一</Option>
                        <Option value={1}>周二</Option>
                        <Option value={2}>周三</Option>
                        <Option value={3}>周四</Option>
                        <Option value={4}>周五</Option>
                        <Option value={5}>周六</Option>
                        <Option value={6}>周日</Option>
                      </Select>
                    </Form.Item>
                    <Form.Item
                      label="执行时间"
                      name="schedule_time"
                      rules={[{ required: true, message: '请选择执行时间' }]}
                    >
                      <TimePicker format="HH:mm" placeholder="选择时间" />
                    </Form.Item>
                  </>
                );
              }
              
              if (scheduleType === 'interval') {
                return (
                  <Form.Item
                    label="间隔时间（分钟）"
                    name="interval_minutes"
                    rules={[
                      { required: true, message: '请输入间隔时间' },
                      { type: 'number', min: 1, message: '间隔时间必须大于0' }
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={1440}
                      placeholder="间隔分钟数"
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                );
              }
              
              return null;
            }}
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<SaveOutlined />}
              >
                {editingTask ? '更新任务' : '创建任务'}
              </Button>
              <Button
                onClick={() => {
                  setTaskModalVisible(false);
                  setEditingTask(null);
                  taskForm.resetFields();
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Settings;
