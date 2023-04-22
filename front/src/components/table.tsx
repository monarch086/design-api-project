import React, {ReactNode, useEffect, useState} from "react";
import styled, {css} from "styled-components";

export type ColumnTemplate<T> = (row: T) => ReactNode;
export type ColumnData = { id: number | string };

export type Column<T extends ColumnData> = { header?: string, styleClass?: string } &
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
    table-layout: auto;
    height: ${ props => props?.empty ? '100%' : 'none' };
`;

const Td = styled.td<{ top?: boolean }>`
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

const Empty = styled.td<{ top?: boolean }>`
    padding: 0.5rem;
    border-left: 2px solid black;
    border-bottom: 2px solid black;
    border-top: ${ props => props?.top ? '2px solid black' : 'none' };
    
    &:last-child {
        border-right: 2px solid black;
    }
`;

const Th = styled.th`
    top: 0;
    padding: 0.5rem;
    background: white;
    position: sticky;
    border: 2px solid black;
    border-right: none;
    
    &:last-child {
        border-right: 2px solid black;
    }
`;

const Tr = styled.tr``;

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
        loading,
        error
    }: {
        columns: Column<T>[],
        data: T[],
        loading: boolean,
        error: boolean,
    }) {
    const [dots, setDots] = useState(0);

    const createRow = (row: T) => columns.map((column, idx) =>
        <Td key={idx} className={column?.styleClass}>
            {'body' in column ? column.body(row) : `${row[column.key]}`}
        </Td>);

    const body = data.map(row => <Tr key={row.id}>{createRow(row)}</Tr>);
    const header = columns.map(({header}, idx) => <Th key={idx}>{header}</Th>);

    const empty = <Tr>
        <Empty colSpan={columns.length || 1}>Empty</Empty>
    </Tr>;

    const loadingTemplate = <Tr>
        <Empty colSpan={columns.length || 1}>Loading{'.'.repeat(dots)}</Empty>
    </Tr>;

    useEffect(() => {
        const intervalId = setInterval(() => {
            setDots((dots) => (dots + 1) % 4);
        }, 500);
        return () => clearInterval(intervalId);
    }, []);

    return <TableContainer>
        <StyledTable empty={!data?.length}>
            <Thead>
            <Tr>{header}</Tr>
            </Thead>
            <Tbody>{loading ? loadingTemplate : (data?.length ? body : empty)}</Tbody>
            <Foot>
            <Tr>
                <Td top colSpan={columns.length || 1}>
                    {error ? 'Error loading data' : `${loading ? 0 : data.length} items`}
                </Td>
            </Tr>
            </Foot>
        </StyledTable>
    </TableContainer>
}

export default Table;
