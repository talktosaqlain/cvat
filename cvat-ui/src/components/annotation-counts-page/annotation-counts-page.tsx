// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import './styles.scss';

import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Row, Col } from 'antd/lib/grid';
import Button from 'antd/lib/button';
import Empty from 'antd/lib/empty';
import Switch from 'antd/lib/switch';
import Result from 'antd/lib/result';
import Title from 'antd/lib/typography/Title';
import Text from 'antd/lib/typography/Text';
import {
    Chart as ChartJS, BarElement, CategoryScale, Legend, LinearScale, Tooltip,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

import { getCore } from 'cvat-core-wrapper';
import GoBackButton from 'components/common/go-back-button';
import CVATLoadingSpinner from 'components/common/loading-spinner';

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip);

const core = getCore();
const BAR_HEIGHT = 22;
const SHAPE_TYPE_COLORS = [
    '#1677ff', '#fa8c16', '#52c41a', '#eb2f96', '#722ed1', '#13c2c2', '#faad14', '#8c8c8c',
];

interface LabelCount {
    id: number;
    name: string;
    color: string;
    count: number;
    by_shape_type?: Record<string, number>;
}

interface AnnotationCounts {
    task_id: number;
    total: number;
    labels: LabelCount[];
}

function AnnotationCountsPage(): JSX.Element {
    const { tid } = useParams<{ tid: string }>();
    const [counts, setCounts] = useState<AnnotationCounts | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [byShapeType, setByShapeType] = useState(false);

    const fetchCounts = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await core.server.request(
                `${core.config.backendAPI}/test/tasks/${tid}/annotation-counts`,
                { method: 'GET', params: byShapeType ? { group_by: 'shape_type' } : {} },
            );
            setCounts(response.data);
        } catch (err: unknown) {
            setCounts(null);
            setError(err instanceof Error ? err.message : String(err));
        } finally {
            setLoading(false);
        }
    }, [tid, byShapeType]);

    useEffect(() => {
        fetchCounts();
    }, [fetchCounts]);

    let content: JSX.Element;
    if (loading) {
        content = <CVATLoadingSpinner />;
    } else if (error !== null) {
        content = (
            <Result
                className='cvat-annotation-counts-error'
                status='error'
                title='Could not load annotation counts'
                subTitle={error}
                extra={<Button type='primary' onClick={fetchCounts}>Try again</Button>}
            />
        );
    } else if (!counts || counts.total === 0) {
        content = (
            <Empty
                className='cvat-annotation-counts-empty'
                description='This task has no annotations yet'
            />
        );
    } else {
        const labels = counts.labels.filter((label) => label.count > 0);
        const shapeTypes = [...new Set(labels.flatMap((label) => Object.keys(label.by_shape_type ?? {})))];
        const datasets = byShapeType ? shapeTypes.map((shapeType, index) => ({
            label: shapeType,
            data: labels.map((label) => label.by_shape_type?.[shapeType] ?? 0),
            backgroundColor: SHAPE_TYPE_COLORS[index % SHAPE_TYPE_COLORS.length],
        })) : [{
            label: 'annotations',
            data: labels.map((label) => label.count),
            backgroundColor: labels.map((label) => label.color),
        }];
        content = (
            <>
                <Text className='cvat-annotation-counts-total'>
                    {`${counts.total} annotations across ${labels.length} labels`}
                </Text>
                <div style={{ height: labels.length * BAR_HEIGHT + 40 }}>
                    <Bar
                        data={{
                            labels: labels.map((label) => label.name),
                            datasets,
                        }}
                        options={{
                            indexAxis: 'y',
                            maintainAspectRatio: false,
                            plugins: { legend: { display: byShapeType } },
                            scales: {
                                x: { stacked: true },
                                y: { stacked: true, ticks: { autoSkip: false } },
                            },
                        }}
                    />
                </div>
            </>
        );
    }

    return (
        <Row className='cvat-annotation-counts-page' justify='center'>
            <Col md={22} lg={20} xl={18} xxl={16}>
                <GoBackButton />
                <Title level={4} className='cvat-annotation-counts-title'>
                    {`Annotation counts for task #${tid}`}
                </Title>
                <div className='cvat-annotation-counts-controls'>
                    <Switch checked={byShapeType} onChange={setByShapeType} />
                    <Text>Split by shape type</Text>
                </div>
                {content}
            </Col>
        </Row>
    );
}

export default React.memo(AnnotationCountsPage);
