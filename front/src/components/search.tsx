import React, {useEffect, useState} from "react";
import useDebounce from "../debounce";
import styled from "styled-components";

const ClearBtn = styled.div`
    position: absolute;
    right: 0.75rem;
    display: none;
    cursor: pointer;
    
    &:after{
        display: inline-block;
        font-size: 1.5em;
        content: "\\00d7";
        height: 31px;
    }
`;

const Input = styled.input`
    padding: 0.5rem;
    border: 2px solid grey;
    outline: none;
    border-radius: 4px;
    font-size: 1em;
`;

const SearchInput = styled.span`
    position: relative;
    display: flex;
    height: 40px;
    align-items: center;
`;

const SearchContainer = styled.div`
    align-self: flex-start;
    
    &:hover ${ClearBtn} {
        display: block;
    }
`;

function Search({ search }: { search: (value: string) => void }) {
    const [value, setValue] = useState('');
    const debouncedValue = useDebounce<string>(value, 500);

    useEffect(() => {
        if (debouncedValue?.length >= 3) {
            search(debouncedValue);
        }
    }, [debouncedValue])

    const input = (val: string) => {
        if (val?.length <= 0) {
            search('');
        }
        setValue(val);
    }

    return <SearchContainer>
        <span>Search</span>
        <SearchInput>
            <Input autoComplete="off" value={value} onChange={event => input(event.target.value)}></Input>
            { value?.length ? <ClearBtn onClick={() => {
                setValue('');
                search('');
            }}></ClearBtn> : null }
        </SearchInput>
    </SearchContainer>
}

export default Search;