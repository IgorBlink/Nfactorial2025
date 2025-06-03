import type { FC } from "react";
import type React from "react";

interface ButtonProps extends React.HtmlHTMLAttributes<HTMLButtonElement>{
    onClick: () => void;

}

export const Button: FC<ButtonProps> = (props: ButtonProps) => {
    return(
        <button {...props}></button>
    )
    
    
}