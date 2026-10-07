// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import './styles.scss';

import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Row, Col } from 'antd/lib/grid';
import Button from 'antd/lib/button';
import Empty from 'antd/lib/empty';
import Result from 'antd/lib/result';
import Title from 'antd/lib/typography/Title';
import Text from 'antd/lib/typography/Text';
import {
    Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

import { getCore } from 'cvat-core-wrapper';
import GoBackButton from 'components/common/go-back-button';
import CVATLoadingSpinner from 'components/common/loading-spinner';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip);

const core = getCore();
const BAR_HEIGHT = 22;

interface LabelCount {
    id: number;
    name: string;
    color: string;
    count: number;
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

    const fetchCounts = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await core.server.request(
                `${core.config.backendAPI}/test/tasks/${tid}/annotation-counts`,
                { method: 'GET' },
            );
            setCounts(response.data);
        } catch (err: unknown) {
            setCounts(null);
            setError(err instanceof Error ? err.message : String(err));
        } finally {
            setLoading(false);
        }
    }, [tid]);

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
        content = (
            <>
                <Text className='cvat-annotation-counts-total'>
                    {`${counts.total} annotations across ${labels.length} labels`}
                </Text>
                <div style={{ height: labels.length * BAR_HEIGHT + 40 }}>
                    <Bar
                        data={{
                            labels: labels.map((label) => label.name),
                            datasets: [{
                                data: labels.map((label) => label.count),
                                backgroundColor: labels.map((label) => label.color),
                            }],
                        }}
                        options={{
                            indexAxis: 'y',
                            maintainAspectRatio: false,
                            plugins: { tooltip: { enabled: true } },
                            scales: { y: { ticks: { autoSkip: false } } },
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
                {content}
            </Col>
        </Row>
    );
}

export default React.memo(AnnotationCountsPage);
