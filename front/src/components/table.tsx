import React, {ReactNode, useEffect, useState} from "react";
import styled, {css} from "styled-components";

export type ColumnTemplate<T> = (row: T) => ReactNode;
export type ColumnData = { id: number | string };

export type Column<T extends ColumnData> = { header?: string } &
    ({ body: ColumnTemplate<T> } | { key: keyof T & (string | number) });

const TableContainer = styled.div`
    height: 100%;
    width: 100%;
    overflow: auto;
    border-top: none;
    position: relative;   
`;


const StyledTable = styled.table<{ empty: boolean }>`
    width: 100%;
    border-spacing: 0;
    table-layout: fixed;
    height: ${ props => props?.empty ? '100%' : 'none' };
`;

const Td = styled.td<{ top?: boolean }>`
    padding: 0.5rem;
    border-left: 2px solid black;
    border-bottom: 2px solid black;
    border-top: ${ props => props?.top ? '2px solid black' : 'none' };
    
    &:last-child {
        border-right: 2px solid black;
    }
`;

const Thead = styled.thead`
    tr:last-child td {
        border-bottom: none;
    }
`;

const Tbody = styled.tbody`
    border-right: 2px solid black;
    
    tr:last-child td {
        border-bottom: none;
    }
`;


const Th = styled.th`
    top: 0;
    background: white;
    position: sticky;
    border: 2px solid black;
    border-right: none;
    
    &:last-child {
        border-right: 2px solid black;
    }
`;

const Tr = styled.tr`
    height: 40px;
`;

const Foot = styled.tfoot`
    width: 100%;
    position: sticky;
    bottom: 0;
    background: white;
`;

function Table<T extends ColumnData>(
    {
        columns,
        data,
        loadMore,
        rowClick,
        loading,
        additionalLoading,
        error,
        threshold = 10.0
    }: {
        columns: Column<T>[],
        data: T[],
        rowClick?: (data: T, ev: React.MouseEvent) => void,
        loadMore?: (count: number) => void,
        loading: boolean,
        error: boolean,
        additionalLoading: boolean,
        threshold?: number
    }) {
    const [dots, setDots] = useState(0);

    const createRow = (row: T) => columns.map((column, idx) =>
        <Td key={idx} onClick={ev => rowClick?.(row, ev)}>
            {'body' in column ? column.body(row) : `${row[column.key]}`}
        </Td>);

    const body = data.map(row => <Tr key={row.id}>{createRow(row)}</Tr>);
    const header = columns.map(({header}, idx) => <Th key={idx}>{header}</Th>);

    const scroll = (event: React.UIEvent) => {
        if (loading || additionalLoading) {
            return;
        }
        const element = event.target as HTMLElement;
        const scrolled = Math.abs(element.scrollHeight - element.scrollTop - element.clientHeight) <= threshold;
        if (scrolled) {
            loadMore && loadMore(loading ? 0 : data.length);
        }
    }
    const empty = <Tr>
        <Td colSpan={columns.length || 1}>Empty</Td>
    </Tr>;

    const loadingTemplate = <Tr>
        <Td colSpan={columns.length || 1}>Loading{'.'.repeat(dots)}</Td>
    </Tr>;

    useEffect(() => {
        const intervalId = setInterval(() => {
            setDots((dots) => (dots + 1) % 4);
        }, 500);
        return () => clearInterval(intervalId);
    }, []);

    return <TableContainer onScroll={scroll}>
        <StyledTable empty={!data?.length}>
            <Thead>
            <Tr>{header}</Tr>
            </Thead>
            <Tbody>{loading ? loadingTemplate : (data?.length ? body : empty)}</Tbody>
            <Foot>
            <Tr>
                <Td top colSpan={columns.length || 1}>
                    {additionalLoading ? 'Loading...' : (error ? 'Error loading data' : `${loading ? 0 : data.length} items`)}
                </Td>
            </Tr>
            </Foot>
        </StyledTable>
    </TableContainer>
}

export default Table;