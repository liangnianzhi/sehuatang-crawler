import React, { useState, useEffect } from 'react';
import { Card, Form, Select, InputNumber, Radio, Button, message, Space, Divider, Input, Switch } from 'antd';
import { PlayCircleOutlined, InfoCircleOutlined, SettingOutlined } from '@ant-design/icons';

const { Option } = Select;

const CrawlForm = ({ onStartTask, loading }) => {
  const [form] = Form.useForm();
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [useProxy, setUseProxy] = useState(false);
  const [proxyConfig, setProxyConfig] = useState({ proxy_enabled: false, proxy_url: '' });

  // 获取主题列表和代理配置
  useEffect(() => {
    fetchThemes();
    fetchProxyConfig();
  }, []);

  const fetchProxyConfig = async () => {
    try {
      const response = await fetch('/api/proxy/config');
      const data = await response.json();
      if (data.success) {
        setProxyConfig(data.data);
        setUseProxy(data.data.proxy_enabled);
        if (data.data.proxy_enabled && data.data.proxy_url) {
          form.setFieldsValue({ proxy: data.data.proxy_url });
        }
      }
    } catch (error) {
      console.error('获取代理配置失败:', error);
    }
  };

  const fetchThemes = async () => {
    try {
      const response = await fetch('/api/themes');
      const data = await response.json();
      if (data.success) {
        setThemes(data.data);
      }
    } catch (error) {
      console.error('获取主题列表失败:', error);
      message.error('获取主题列表失败');
    }
  };

  // 处理主题选择变化
  const handleThemeChange = (value) => {
    setSelectedTheme(themes.find(theme => theme.id === value));
    form.setFieldsValue({ mode: '1', start_page: 1, end_page: 1 });
  };

  // 处理模式变化
  const handleModeChange = (e) => {
    if (e.target.value === '2') {
      form.setFieldsValue({ start_page: 1, end_page: 1 });
    }
  };

  // 保存代理配置
  const saveProxyConfig = async (enabled, proxyUrl = '') => {
    try {
      const response = await fetch('/api/proxy/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enabled: enabled,
          proxy_url: proxyUrl
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

  // 提交表单
  const handleSubmit = async (values) => {
    try {
      // 处理代理设置
      const taskData = {
        ...values,
        proxy: useProxy ? values.proxy : ''
      };
      
      // 保存代理配置
      if (useProxy && values.proxy) {
        await saveProxyConfig(true, values.proxy);
      }
      
      const result = await onStartTask(taskData);
      if (result.success) {
        message.success('爬取任务已启动！');
        form.resetFields();
        setSelectedTheme(null);
        // 不重置代理设置，保持持久化
        if (proxyConfig.proxy_enabled) {
          setUseProxy(true);
          form.setFieldsValue({ proxy: proxyConfig.proxy_url });
        }
      } else {
        message.error(result.error || '启动任务失败');
      }
    } catch (error) {
      message.error('启动任务失败');
    }
  };

  // 获取主题选项
  const getThemeOptions = () => {
    return themes.map(theme => (
      <Option key={theme.id} value={theme.id}>
        <Space>
          <span>{theme.name}</span>
          {theme.supports_hot && (
            <span style={{ color: '#52c41a', fontSize: '12px' }}>
              (支持热门)
            </span>
          )}
        </Space>
      </Option>
    ));
  };

  return (
    <Card 
      title={
        <Space>
          <PlayCircleOutlined />
          新建爬取任务
        </Space>
      }
      style={{ marginBottom: 24 }}
      extra={
        <InfoCircleOutlined 
          style={{ color: '#1890ff', cursor: 'pointer' }}
          onClick={() => message.info('选择主题和模式，开始爬取磁力链接')}
        />
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          mode: '1',
          start_page: 1,
          end_page: 1
        }}
      >
        <Form.Item
          label="选择主题"
          name="theme_id"
          rules={[{ required: true, message: '请选择主题' }]}
        >
          <Select
            placeholder="请选择要爬取的主题"
            onChange={handleThemeChange}
            showSearch
            filterOption={(input, option) =>
              option.children.props.children[0].props.children.toLowerCase().includes(input.toLowerCase())
            }
          >
            {getThemeOptions()}
          </Select>
        </Form.Item>

        <Form.Item
          label="爬取模式"
          name="mode"
          rules={[{ required: true, message: '请选择爬取模式' }]}
        >
          <Radio.Group onChange={handleModeChange}>
            <Space direction="vertical">
              <Radio value="1">
                <Space>
                  <span>普通模式</span>
                  <span style={{ color: '#666', fontSize: '12px' }}>
                    爬取指定页面的内容
                  </span>
                </Space>
              </Radio>
              <Radio 
                value="2" 
                disabled={!selectedTheme?.supports_hot}
              >
                <Space>
                  <span>热门模式</span>
                  <span style={{ color: '#666', fontSize: '12px' }}>
                    爬取热门内容（仅部分主题支持）
                  </span>
                </Space>
              </Radio>
            </Space>
          </Radio.Group>
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.mode !== currentValues.mode}
        >
          {({ getFieldValue }) => {
            const mode = getFieldValue('mode');
            if (mode === '1') {
              return (
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
                    <span style={{ color: '#666', fontSize: '12px' }}>
                      (1-100页)
                    </span>
                  </Space>
                </Form.Item>
              );
            }
            return null;
          }}
        </Form.Item>

        <Divider />

        <Form.Item label="代理设置">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Switch 
                checked={useProxy} 
                onChange={setUseProxy}
                checkedChildren="启用"
                unCheckedChildren="禁用"
              />
              <span>使用代理（国外网站访问需要）</span>
            </Space>
            
            {useProxy && (
              <Form.Item
                name="proxy"
                noStyle
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
                  style={{ width: '100%' }}
                  prefix={<SettingOutlined />}
                />
              </Form.Item>
            )}
          </Space>
        </Form.Item>

        <Divider />

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<PlayCircleOutlined />}
              size="large"
            >
              开始爬取
            </Button>
            <Button
              onClick={() => {
                form.resetFields();
                setSelectedTheme(null);
                // 保持代理设置
                if (proxyConfig.proxy_enabled) {
                  setUseProxy(true);
                  form.setFieldsValue({ proxy: proxyConfig.proxy_url });
                }
              }}
              size="large"
            >
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>

      {selectedTheme && (
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          background: '#f6ffed', 
          border: '1px solid #b7eb8f', 
          borderRadius: 6 
        }}>
          <Space>
            <InfoCircleOutlined style={{ color: '#52c41a' }} />
            <span>
              已选择：<strong>{selectedTheme.name}</strong>
              {selectedTheme.supports_hot && ' (支持热门模式)'}
            </span>
          </Space>
        </div>
      )}
    </Card>
  );
};

export default CrawlForm;

