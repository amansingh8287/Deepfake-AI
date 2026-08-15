import { render, screen } from "@testing-library/react";
import { UploadZone } from "./UploadZone";

describe("UploadZone", () => {
  it("renders the label and helper text", () => {
    render(
      <UploadZone
        accept={{ "image/*": [".png"] }}
        label="Upload a file"
        helper="Only approved formats are accepted."
        onFileSelected={() => undefined}
      />
    );

    expect(screen.getByText("Upload a file")).toBeInTheDocument();
    expect(screen.getByText("Only approved formats are accepted.")).toBeInTheDocument();
  });
});

