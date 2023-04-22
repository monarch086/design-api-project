import React, {PropsWithChildren, useEffect, useRef} from "react";
import styled from "styled-components";

const Modal = styled.dialog`
  padding: 0.75rem;
  width: 400px;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
  border: none;
  border-radius: 3px;
  
  ::backdrop {
    background: rgba(0,0,0,0.05);
  }
`;

const Button = styled.span`
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border: 1px solid lightgrey;
    border-radius: 2px;
    margin-left: auto;
`;

const Row = styled.div`
    display: flex;
    align-items: center;
    width: 100%;
`;

const Title = styled.span`
    font-size: 1em;
    font-weight: bold;
`;

function Dialog({ show, title, time, onClose, children }: PropsWithChildren<{ title: string, show?: boolean, time?: number, onClose?: () => void }>) {

    const dialog = useRef<HTMLDialogElement>(null);

    useEffect(() => {
        console.log(dialog);
        if (show) {
            dialog.current?.showModal();
        } else {
            dialog.current?.close();
        }
    }, [show]);

    const preventAutoClose = (e: React.MouseEvent) => e.stopPropagation();

    return <Modal ref={dialog} onClick={onClose}>
        <div onClick={preventAutoClose}>
            <Row>
                <Title>{ title }</Title>
                <Button onClick={onClose}>Close</Button>
            </Row>
            { children }
        </div>
    </Modal>
}

export default Dialog;