import React, { useState, useEffect } from 'react';
import { Layout, Typography, theme, Card, Space, Tag, Menu } from 'antd';
import { 
  CloudDownloadOutlined, 
  FileTextOutlined, 
  ClockCircleOutlined,
  SettingOutlined,
  HomeOutlined
} from '@ant-design/icons';
import CrawlForm from './components/CrawlForm';
import TaskList from './components/TaskList';
import Settings from './components/Settings';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recentLogs, setRecentLogs] = useState([]);
  const [currentPage, setCurrentPage] = useState('home');
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/tasks');
      const data = await response.json();
      if (data.success) {
        setTasks(data.data);
      }
    } catch (error) {
      console.error('获取任务列表失败:', error);
    }
  };

  // 获取最近日志
  const fetchRecentLogs = async () => {
    try {
      const response = await fetch('/api/logs');
      const data = await response.json();
      if (data.success) {
        setRecentLogs(data.data);
      }
    } catch (error) {
      console.error('获取日志失败:', error);
    }
  };

  // 定期更新任务状态和日志
  useEffect(() => {
    fetchTasks();
    fetchRecentLogs();
    const interval = setInterval(() => {
      fetchTasks();
      fetchRecentLogs();
    }, 2000); // 每2秒更新一次
    return () => clearInterval(interval);
  }, []);

  // 开始新任务
  const startNewTask = async (taskData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });
      const data = await response.json();
      if (data.success) {
        // 刷新任务列表
        setTimeout(fetchTasks, 1000);
      }
      return data;
    } catch (error) {
      console.error('启动任务失败:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  // 删除任务
  const deleteTask = async (taskId) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.success) {
        fetchTasks();
      }
      return data;
    } catch (error) {
      console.error('删除任务失败:', error);
      return { success: false, error: error.message };
    }
  };

  // 下载结果
  const downloadResult = (taskId) => {
    window.open(`/api/download/${taskId}`, '_blank');
  };

  // 菜单项配置
  const menuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ];

  // 渲染页面内容
  const renderPageContent = () => {
    if (currentPage === 'settings') {
      return <Settings />;
    }

    return (
      <>
        <CrawlForm onStartTask={startNewTask} loading={loading} />
        
        {/* 实时日志显示 */}
        <Card 
          title={
            <Space>
              <ClockCircleOutlined />
              实时日志
              <Tag color="blue">{recentLogs.length}</Tag>
            </Space>
          }
          style={{ marginBottom: 24 }}
          bodyStyle={{ 
            maxHeight: '300px', 
            overflow: 'auto',
            padding: '12px'
          }}
        >
          {recentLogs.length > 0 ? (
            <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
              {recentLogs.map((log, index) => (
                <div key={index} style={{ 
                  padding: '2px 0',
                  borderBottom: index < recentLogs.length - 1 ? '1px solid #f0f0f0' : 'none',
                  color: log.includes('ERROR') ? '#ff4d4f' : 
                         log.includes('WARNING') ? '#faad14' : '#666'
                }}>
                  {log}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
              <FileTextOutlined style={{ fontSize: '24px', marginBottom: 8 }} />
              <p>暂无日志记录</p>
            </div>
          )}
        </Card>
        
        <TaskList 
          tasks={tasks} 
          onDeleteTask={deleteTask}
          onDownloadResult={downloadResult}
        />
      </>
    );
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <CloudDownloadOutlined className="header-icon" />
          <Title level={3} className="header-title">
            色花堂磁力链接爬虫工具
          </Title>
        </div>
      </Header>
      
      <Layout>
        <Sider width={200} style={{ background: colorBgContainer }}>
          <Menu
            mode="inline"
            selectedKeys={[currentPage]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => setCurrentPage(key)}
          />
        </Sider>
        
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content className="app-content">
            <div className="content-wrapper" style={{ background: colorBgContainer, borderRadius: borderRadiusLG, padding: 24 }}>
              {renderPageContent()}
            </div>
          </Content>
        </Layout>
      </Layout>
      
      <Footer className="app-footer">
        <div className="footer-content">
          <p>色花堂磁力链接爬虫工具 ©2024 - 仅供学习和研究使用</p>
          <p>请遵守当地法律法规，使用者需自行承担使用风险</p>
        </div>
      </Footer>
    </Layout>
  );
}

export default App;

